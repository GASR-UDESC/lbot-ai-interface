interface CommandPanelProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
  onReset: () => void;
  onToggleCamera: () => void;
  isExecuting: boolean;
  cameraModeLabel: string;
  history: string[];
}

export function CommandPanel({
  value,
  onChange,
  onExecute,
  onReset,
  onToggleCamera,
  isExecuting,
  cameraModeLabel,
  history,
}: CommandPanelProps) {
  return (
    <div className="panel-card">
      <div className="panel-card__header">
        <h2>Comandos LBML</h2>
        <p>Use sequencias como `D40F;R90L;D20F;`.</p>
      </div>

      <label className="field-label" htmlFor="lbml-command">
        Sequencia
      </label>
      <textarea
        id="lbml-command"
        className="command-input"
        rows={5}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="D40F;R90L;D20F;"
      />

      <div className="button-row">
        <button className="primary-button" onClick={onExecute} disabled={isExecuting}>
          Executar
        </button>
        <button className="secondary-button" onClick={onReset}>
          Reset
        </button>
        <button className="secondary-button" onClick={onToggleCamera} disabled={isExecuting}>
          {cameraModeLabel}
        </button>
      </div>

      <div className="history-block">
        <div className="history-block__header">
          <h3>Historico</h3>
        </div>

        {history.length === 0 ? <p className="empty-history">Nenhum comando executado ainda.</p> : null}

        <ul className="history-list">
          {history.map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
