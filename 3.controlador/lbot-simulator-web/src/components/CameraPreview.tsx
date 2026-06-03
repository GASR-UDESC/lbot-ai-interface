import { useEffect, useRef, useState } from 'react';

interface CameraPreviewProps {
  connected: boolean;
  onCanvasReady?: (canvas: HTMLCanvasElement) => (() => void) | void;
}

type PreviewState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'ready' }
  | { kind: 'error'; text: string };

export function CameraPreview({ connected, onCanvasReady }: CameraPreviewProps) {
  const [state, setState] = useState<PreviewState>({ kind: 'idle' });
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const cleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!connected) {
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }
      setState({ kind: 'idle' });
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) {
      setState({ kind: 'error', text: 'Canvas indisponivel.' });
      return;
    }

    setState({ kind: 'loading' });

    if (onCanvasReady) {
      const cleanup = onCanvasReady(canvas);
      if (cleanup) {
        cleanupRef.current = cleanup;
      }
    }

    setState({ kind: 'ready' });

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }
    };
  }, [connected, onCanvasReady]);

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

        <canvas
          ref={canvasRef}
          className="camera-preview-canvas"
          width={400}
          height={300}
          style={{
            display: state.kind === 'ready' ? 'block' : 'none',
          }}
        />
      </div>
    </div>
  );
}
