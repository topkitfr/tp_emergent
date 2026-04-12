import React from 'react';

export default class ErrorBoundary extends React.Component {
  state = { error: null };
  componentDidCatch(error, info) {
    console.error('=== REACT ERROR BOUNDARY ===');
    console.error('Error:', error.message);
    console.error('Component stack:', info.componentStack);
  }
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) return (
      <div style={{padding:20,color:'red'}}>
        <b>Crash: {this.state.error.message}</b>
        <pre style={{fontSize:11}}>{this.state.error.stack}</pre>
      </div>
    );
    return this.props.children;
  }
}
