export function TopNav() {
  return (
    <nav className="top-nav">
      <h1 className="top-nav__title">LBot Simulator Web</h1>
      <div className="top-nav__callout">
        <span className="top-nav__callout-label">HTTP</span>
        <code>POST /api/commands</code>
        <code>POST /api/reset</code>
      </div>
    </nav>
  );
}
