import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'red' }}>
          <h2>Something went wrong</h2>
          <pre style={{ color: 'red', background: '#f5f5f5', padding: '10px' }}>
            {this.state.error && this.state.error.toString()}
          </pre>
          {this.state.errorInfo && (
            <pre style={{ color: 'red', background: '#f5f5f5', padding: '10px' }}>
              {this.state.errorInfo.componentStack}
            </pre>
          )}
          <button onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;