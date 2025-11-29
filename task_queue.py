"""
Background task queue for handling long-running operations asynchronously
"""
import threading
import time
import logging
from queue import Queue, Empty
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger("task_queue")

# Global task manager instance
_task_manager = None

@dataclass
class TaskResult:
    """Result of a completed task"""
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: int = 0  # percentage 0-100
    message: str = ""
    data: Any = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None
    error: str = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
        }


class TaskQueue:
    """
    Thread-safe queue for background task processing
    Prevents the Flask app from freezing during long-running operations
    """
    
    def __init__(self, num_workers=1):
        """
        Initialize task queue
        
        Args:
            num_workers: Number of worker threads
        """
        self.queue = Queue()
        self.results: Dict[str, TaskResult] = {}
        self.num_workers = num_workers
        self.running = False
        self.worker_threads = []
        
    def start(self):
        """Start worker threads"""
        if self.running:
            return
            
        self.running = True
        for i in range(self.num_workers):
            thread = threading.Thread(target=self._worker_loop, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
        logger.info(f"Task queue started with {self.num_workers} workers")
    
    def stop(self):
        """Stop all worker threads"""
        self.running = False
        for thread in self.worker_threads:
            thread.join(timeout=5)
        logger.info("Task queue stopped")
    
    def submit_task(self, task_id: str, func: Callable, args=None, kwargs=None) -> str:
        """
        Submit a task to the queue
        
        Args:
            task_id: Unique identifier for the task
            func: Callable function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            task_id
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
            
        # Create task result entry
        self.results[task_id] = TaskResult(
            task_id=task_id,
            status="pending",
            progress=0
        )
        
        # Queue the task
        self.queue.put((task_id, func, args, kwargs))
        logger.info(f"Task {task_id} submitted to queue")
        return task_id
    
    def get_status(self, task_id: str) -> TaskResult:
        """Get the status of a task"""
        return self.results.get(task_id, TaskResult(task_id=task_id, status="not_found"))
    
    def _worker_loop(self):
        """Main worker loop - processes tasks from queue"""
        while self.running:
            try:
                # Get task with timeout to allow graceful shutdown
                task_id, func, args, kwargs = self.queue.get(timeout=1)
                
                # Update status to running
                self.results[task_id].status = "running"
                self.results[task_id].started_at = datetime.utcnow()
                logger.info(f"Task {task_id} started")
                
                try:
                    # Execute the task
                    result = func(*args, **kwargs)
                    
                    # Update result
                    self.results[task_id].status = "completed"
                    self.results[task_id].progress = 100
                    self.results[task_id].data = result
                    self.results[task_id].completed_at = datetime.utcnow()
                    logger.info(f"Task {task_id} completed successfully")
                    
                except Exception as e:
                    # Update with error
                    self.results[task_id].status = "failed"
                    self.results[task_id].error = str(e)
                    self.results[task_id].completed_at = datetime.utcnow()
                    logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                
                self.queue.task_done()
                
            except Empty:
                # No task available, continue waiting
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)


def get_task_queue() -> TaskQueue:
    """Get or create the global task queue instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskQueue(num_workers=2)
        _task_manager.start()
    return _task_manager


def update_task_progress(task_id: str, progress: int, message: str = ""):
    """
    Update task progress from within a task
    
    Args:
        task_id: Task ID
        progress: Progress percentage (0-100)
        message: Status message
    """
    queue = get_task_queue()
    if task_id in queue.results:
        queue.results[task_id].progress = progress
        if message:
            queue.results[task_id].message = message
