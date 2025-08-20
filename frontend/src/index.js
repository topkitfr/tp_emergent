import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import CollaborativeApp from './CollaborativeApp';

const root = ReactDOM.createRoot(document.getElementById('root'));

// Check if we want to use the collaborative version
const useCollaborativeVersion = window.location.search.includes('collaborative') || 
                               localStorage.getItem('use_collaborative') === 'true' ||
                               true; // Default to collaborative for now

if (useCollaborativeVersion) {
  console.log('🚀 Starting TopKit Collaborative App');
  root.render(<CollaborativeApp />);
} else {
  // Fallback to regular app
  const App = require('./App').default;
  const AuthProvider = require('./App').AuthProvider;
  
  root.render(
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
