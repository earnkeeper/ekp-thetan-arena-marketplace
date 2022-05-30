import logging

from listener.listener_container import ListenerContainer

if __name__ == '__main__':
    container = ListenerContainer()

    logging.basicConfig(level=logging.INFO)

    logging.info("🚀 Application Start")

    container.listener_service.listen()
