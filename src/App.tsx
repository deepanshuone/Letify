import { Component, useEffect, type ErrorInfo, type ReactNode } from 'react';
import { Header } from './components/Header';
import { BY_ID } from './data';
import { Landing } from './pages/Landing';
import { ProblemPage } from './pages/ProblemPage';
import { Problems } from './pages/Problems';
import { useRoute } from './router';
import { FiltersProvider } from './state/filters';
import { ProgressProvider } from './state/progress';
import { ToastProvider } from './state/toast';

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack);
  }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="crash">
        <h1>Something went wrong</h1>
        <p className="muted">The page hit an unexpected error. Your saved code and progress are not affected.</p>
        <p>
          <button className="btn primary" onClick={() => location.reload()}>
            Reload the page
          </button>
        </p>
      </div>
    );
  }
}

function Page() {
  const route = useRoute();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [route.name === 'problem' ? route.id : route.name]);
  useEffect(() => {
    if (route.name === 'landing') document.title = 'Letify: free DSA practice';
  }, [route.name]);

  if (route.name === 'problem') {
    const p = BY_ID.get(route.id)!;
    return <ProblemPage key={p.id} p={p} />;
  }
  if (route.name === 'problems') return <Problems />;
  return <Landing />;
}

export function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <ProgressProvider>
          <FiltersProvider>
            <a className="skip" href="#view" onClick={(e) => { e.preventDefault(); document.getElementById('view')?.focus(); }}>
              Skip to content
            </a>
            <Header />
            <main className="wrap" id="view" tabIndex={-1}>
              <Page />
            </main>
          </FiltersProvider>
        </ProgressProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}
