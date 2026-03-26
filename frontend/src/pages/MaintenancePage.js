// frontend/src/pages/MaintenancePage.js
export default function MaintenancePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-950 text-white px-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-6">🔧</div>
        <h1 className="text-3xl font-bold mb-3">Site en maintenance</h1>
        <p className="text-gray-400 mb-8">
          On travaille pour améliorer Topkit. Le site sera de retour très bientôt.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-5 py-2.5 bg-white text-gray-900 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
        >
          Réessayer
        </button>
      </div>
    </div>
  );
}
