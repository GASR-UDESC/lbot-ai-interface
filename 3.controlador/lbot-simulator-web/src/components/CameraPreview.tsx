import { useEffect, useRef, useState } from "react";
import { getCamera, getState } from "../lib/api.js";

export function CameraPreview({ connected }: { connected: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState("Aguardando câmera.");
  useEffect(() => {
    let disposed = false,
      fetching = false;
    setReady(false);
    setStatus(connected ? "Carregando câmera…" : "Servidor desconectado.");
    if (!connected) return;
    const update = async () => {
      if (fetching || disposed) return;
      fetching = true;
      try {
        const data = await getCamera();
        if (!data.image) throw new Error("camera_unavailable");
        const current = await getState();
        if (data.session_id !== current.state.session_id)
          throw new Error("Captura de uma sessão anterior.");
        const image = new Image();
        image.src = `data:image/png;base64,${data.image}`;
        await image.decode();
        if (!disposed) {
          canvasRef.current?.getContext("2d")?.drawImage(image, 0, 0, 640, 480);
          setReady(true);
          setStatus(
            `Quadro ${data.frame_id.slice(0, 8)} · revisão ${data.revision} · ${data.captured_at}`,
          );
        }
      } catch (error) {
        if (!disposed) {
          setReady(false);
          setStatus(
            error instanceof Error ? error.message : "camera_unavailable",
          );
          canvasRef.current?.getContext("2d")?.clearRect(0, 0, 640, 480);
        }
      } finally {
        fetching = false;
      }
    };
    void update();
    const timer = setInterval(() => void update(), 1000);
    return () => {
      disposed = true;
      clearInterval(timer);
    };
  }, [connected]);
  return (
    <div className="camera-preview-card">
      <div className="camera-preview-header">
        <h3>Visão do robô</h3>
      </div>
      <div className="camera-preview-frame">
        {!ready && (
          <div className="camera-preview-placeholder">
            <p role="status">{status}</p>
          </div>
        )}
        <canvas
          ref={canvasRef}
          className={`camera-preview-canvas ${ready ? "" : "camera-preview-canvas--hidden"}`}
          width={640}
          height={480}
        />
      </div>
      {ready && <small>{status}</small>}
    </div>
  );
}
