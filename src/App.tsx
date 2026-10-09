import { Component, useEffect, type ErrorInfo, type ReactNode } from 'react';
import { Header } from './components/Header';
import { BY_ID } from './data';
import { ContestPage } from './pages/Contest';
import { Landing } from './pages/Landing';
import { Plans, PlanDetail } from './pages/Plans';
import { ProblemPage } from './pages/ProblemPage';
import { Problems } from './pages/Problems';
import { Profile } from './pages/Profile';
import { useRoute } from './router';
import type { CloudBackend } from './user/sync';
import { AuthDialogProvider } from './state/authdialog';
import { CloudProvider } from './state/cloud';
import { ContestProvider } from './state/contest';
import { FiltersProvider } from './state/filters';
import { ToastProvider } from './state/toast';
import { UserDataProvider } from './state/userdata';

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
  if (route.name === 'plans') return <Plans />;
  if (route.name === 'plan') return <PlanDetail id={route.id} />;
  if (route.name === 'profile') return <Profile />;
  if (route.name === 'contest') return <ContestPage />;
  return <Landing />;
}

/** `backendFactory` lets tests plug in a fake cloud; in production the Supabase backend is used when configured. */
export function App({ backendFactory }: { backendFactory?: () => Promise<CloudBackend> } = {}) {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <UserDataProvider>
          <CloudProvider backendFactory={backendFactory}>
            <ContestProvider>
              <AuthDialogProvider>
                <FiltersProvider>
                  <a className="skip" href="#view" onClick={(e) => { e.preventDefault(); document.getElementById('view')?.focus(); }}>
                    Skip to content
                  </a>
                  <Header />
                  <main className="wrap" id="view" tabIndex={-1}>
                    <Page />
                  </main>
                </FiltersProvider>
              </AuthDialogProvider>
            </ContestProvider>
          </CloudProvider>
        </UserDataProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}
