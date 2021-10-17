import logging

import uvicorn as uvicorn
from core import context_logger

logger = context_logger.get(__name__)

if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host='0.0.0.0',
        port=8000,
        log_level=logging.DEBUG,
        reload=True
    )
