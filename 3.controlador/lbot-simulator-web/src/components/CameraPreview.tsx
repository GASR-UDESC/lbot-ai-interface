import { useEffect, useRef, useState } from 'react';
import { getCamera } from '../lib/api.js';

interface CameraPreviewProps {
  connected: boolean;
}

type PreviewState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'image'; src: string }
  | { kind: 'error'; text: string };

const POLL_MS = 2000;

export function CameraPreview({ connected }: CameraPreviewProps) {
  const [state, setState] = useState<PreviewState>({ kind: 'idle' });
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const fetchImage = async () => {
      setState((prev) => (prev.kind === 'image' ? prev : { kind: 'loading' }));

      try {
        const response = await getCamera();

        if (!response.connected || !response.image) {
          setState({
            kind: 'error',
            text: response.error ?? 'Camera do robo indisponivel',
          });
          return;
        }

        setState({ kind: 'image', src: `data:image/png;base64,${response.image}` });
      } catch {
        setState({ kind: 'error', text: 'Falha ao buscar imagem da camera.' });
      }
    };

    if (!connected) {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }

      setState({ kind: 'idle' });
      return;
    }

    void fetchImage();
    timerRef.current = window.setInterval(() => void fetchImage(), POLL_MS);

    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [connected]);

  return (
    <div className="camera-preview-card">
      <div className="camera-preview-header">
        <h3>Visao do Robo</h3>
        {state.kind === 'loading' && <span className="camera-preview-loading" />}
      </div>

      <div className="camera-preview-frame">
        {state.kind === 'idle' && (
          <div className="camera-preview-placeholder">
            <p>Conecte o simulador para visualizar a camera.</p>
          </div>
        )}

        {state.kind === 'loading' && (
          <div className="camera-preview-placeholder">
            <p>Carregando visao...</p>
          </div>
        )}

        {state.kind === 'error' && (
          <div className="camera-preview-placeholder camera-preview-placeholder--error">
            <p>{state.text}</p>
          </div>
        )}

        {state.kind === 'image' && (
          <img
            className="camera-preview-image"
            src={state.src}
            alt="Visao do robo"
          />
        )}
      </div>
    </div>
  );
}
