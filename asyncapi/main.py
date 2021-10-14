import logging

import uvicorn as uvicorn
from core.logger import LOGGING

if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
