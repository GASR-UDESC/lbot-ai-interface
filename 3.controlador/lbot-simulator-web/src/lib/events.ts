import type { ServerEvent } from '../../shared/protocol.js';

export interface EventConnection {
  close: () => void;
}

export function connectToServerEvents(handlers: {
  onEvent: (event: ServerEvent) => void;
  onError: () => void;
}): EventConnection {
  const source = new EventSource('/api/events');

  source.onmessage = (message) => {
    const event = JSON.parse(message.data) as ServerEvent;
    handlers.onEvent(event);
  };

  source.onerror = () => {
    handlers.onError();
  };

  return {
    close() {
      source.close();
    },
  };
}
