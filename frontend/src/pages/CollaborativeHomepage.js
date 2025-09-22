import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const CollaborativeHomepage = ({ user, teams, brands, players, masterJerseys, onViewChange, API }) => {
  const navigate = useNavigate();
  
  // New state for dynamic homepage data
  const [expensiveKits, setExpensiveKits] = useState([]);
  const [recentMasterKits, setRecentMasterKits] = useState([]);
  const [recentContributions, setRecentContributions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Load dynamic homepage data
  useEffect(() => {
    loadHomepageData();
  }, []);

  const loadHomepageData = async () => {
    setLoading(true);
    try {
      const [expensiveRes, recentMasterRes, recentContribRes] = await Promise.all([
        fetch(`${API}/api/homepage/expensive-kits?limit=5`),
        fetch(`${API}/api/homepage/recent-master-kits?limit=6`),
        fetch(`${API}/api/homepage/recent-contributions?limit=10`)
      ]);

      if (expensiveRes.ok) {
        const expensiveData = await expensiveRes.json();
        setExpensiveKits(expensiveData);
      }

      if (recentMasterRes.ok) {
        const recentMasterData = await recentMasterRes.json();
        setRecentMasterKits(recentMasterData);
      }

      if (recentContribRes.ok) {
        const recentContribData = await recentContribRes.json();
        setRecentContributions(recentContribData);
      }
    } catch (error) {
      console.error('Error loading homepage data:', error);
    }
    setLoading(false);
  };

  // Handle user profile click
  const handleUserClick = (userId) => {
    if (user) {
      navigate(`/profile/${userId}`);
    } else {
      // Store the intended action and show login modal
      localStorage.setItem('pendingAction', JSON.stringify({
        action: 'viewProfile',
        userId: userId
      }));
      // Trigger login modal via parent component
      if (typeof onViewChange === 'function') {
        // For now, navigate to home and let user manually login
        navigate('/');
      }
    }
  };

  const recentTeams = teams?.slice().reverse().slice(0, 10) || []; // Show latest teams first (reverse order)
  const recentBrands = brands?.slice(0, 4) || [];
  const recentMasterJerseys = masterJerseys?.slice(0, 12) || [];
  // Statistics
  const stats = [
    { label: 'Teams', value: teams?.length || 0, icon: '⚽', color: 'text-gray-900' },
    { label: 'Brands', value: brands?.length || 0, icon: '👕', color: 'text-gray-900' },
    { label: 'Players', value: players?.length || 0, icon: '👤', color: 'text-gray-900' },
    { label: 'Kits', value: masterJerseys?.length || 0, icon: '📋', color: 'text-gray-900' }
  ];

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section - TopKit Narrative with Background Banner */}
      <div 
        className="bg-white py-16 md:py-24 relative bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgb(255, 255, 255), rgba(255, 255, 255, 0)), url('https://customer-assets.emergentagent.com/job_footwear-collab/artifacts/3cir86pr_EmzagksXIAg35Ia.jpg')`
        }}
      >
        <div className="max-w-6xl mx-auto px-4 text-center relative z-10">
          <div className="mb-6">
            <div className="bg-white px-6 py-3 mb-4 inline-block">
              <h1 className="text-4xl md:text-6xl font-bold leading-tight akira-font m-0" style={{color: 'rgb(17, 24, 39)'}}>
                VALUE YOUR COLLECTION
              </h1>
            </div>
            <br />
            <div className="bg-white px-6 py-3 inline-block">
              <h2 className="text-4xl md:text-6xl font-bold leading-tight akira-font m-0" style={{color: 'rgb(75, 85, 99)'}}>
                OF FOOTBALL KITS
              </h2>
            </div>
          </div>
          
          <div className="mb-8">
            <div className="bg-white px-6 py-3 inline-block">
              <p className="text-lg md:text-xl m-0" style={{color: 'rgb(75, 85, 99)'}}>
                Discover the value of your kits with TopKit, <br />
                the world's most complete collaborative <br />
                database on football
              </p>
            </div>
          </div>
          
          {/* CTA Buttons - TopKit Focus - Removed Documenter button */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={() => navigate('/kit-area')}
              className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-full font-semibold transition-all text-lg"
            >
              Create your collection
            </button>
          </div>
        </div>
      </div>

      {/* Categories Carousel - Like WhenToCop top brands */}
      <div className="py-8 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex overflow-x-auto space-x-4 pb-4" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
            {recentTeams.map((team, index) => (
              <button
                key={team.id}
                onClick={() => navigate('/catalogue')}
                className="flex-shrink-0 bg-white rounded-lg p-4 hover:shadow-md transition-all border border-gray-100 w-[120px] h-[120px] flex flex-col items-center justify-center"
              >
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-2 overflow-hidden">
                  {team.logo_url ? (
                    <img 
                      src={team.logo_url.startsWith('data:') || team.logo_url.startsWith('http') 
                        ? team.logo_url 
                        : team.logo_url.startsWith('image_uploaded_')
                          ? `${API}/api/legacy-image/${team.logo_url}`
                          : `${API}/api/${team.logo_url}`}
                      alt={team.name || 'Unknown Team'}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-xl" style={{display: team.logo_url ? 'none' : 'flex'}}>⚽</span>
                </div>
                <div className="font-medium text-sm text-gray-900 text-center w-full overflow-hidden">
                  <span className="block truncate" title={team.name || 'Unknown Team'}>
                    {team.name && team.name.length > 12 ? `${team.name.substring(0, 9)}...` : (team.name || 'Unknown Team')}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Most wanted kits Section - TopKit Focus */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Most wanted kits</h2>
            <button
              onClick={() => onViewChange('kit-area')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              All kits
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.map((jersey, index) => (
              <div
                key={jersey.id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                onClick={() => onViewChange('kit-area')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                  {jersey.front_photo_url ? (
                    <img 
                      src={jersey.front_photo_url.startsWith('data:') || jersey.front_photo_url.startsWith('http') ? jersey.front_photo_url : 
                           jersey.front_photo_url.startsWith('uploads/') ? 
                           `${API}/api/${jersey.front_photo_url}` :
                           `${API}/api/uploads/master_kits/${jersey.front_photo_url}.jpg`}
                      alt={`${jersey.club_name || jersey.club || 'Team'} ${jersey.season}`}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-4xl" style={{display: jersey.front_photo_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {jersey.club_name || jersey.club || 'Unknown team'}
                  </h3>
                  <p className="text-xs text-gray-500 mb-2">{jersey.season}</p>
                  <p className="text-sm font-semibold text-gray-900">
                    Estimated value<br />
                    <span className="text-lg">120€</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Latest database contributions Section - Updated to show recent master kits */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              Latest database contributions 🔥
            </h2>
            <button
              onClick={() => onViewChange('kit-area')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              View all kits
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterKits.slice(0, 6).map((kit, index) => (
              <div
                key={kit.id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                onClick={() => onViewChange('kit-area')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                  {kit.front_photo_url ? (
                    <img 
                      src={kit.front_photo_url.startsWith('data:') || kit.front_photo_url.startsWith('http') ? kit.front_photo_url : 
                           kit.front_photo_url.startsWith('uploads/') ? 
                           `${API}/api/${kit.front_photo_url}` :
                           `${API}/api/uploads/master_kits/${kit.front_photo_url}.jpg`}
                      alt={`${kit.club_name || kit.club || 'Team'} ${kit.season}`}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-4xl" style={{display: kit.front_photo_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {kit.club_name || kit.club || 'Unknown team'}
                  </h3>
                  <p className="text-xs text-gray-500 mb-2">{kit.season}</p>
                  <p className="text-sm text-green-600">
                    <span className="text-lg font-bold">Recently added ✓</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Rare and sought-after kits - Updated to show most expensive from collections */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Rare and sought-after kits</h2>
            <button
              onClick={() => onViewChange('kit-area')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              View more rare kits
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {expensiveKits.map((item, index) => (
              <div
                key={item.collection_id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100 relative"
                onClick={() => onViewChange('kit-area')}
              >
                <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-bold">
                  RARE
                </div>
                <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                  {item.master_kit.front_photo_url ? (
                    <img 
                      src={item.master_kit.front_photo_url.startsWith('data:') || item.master_kit.front_photo_url.startsWith('http') ? item.master_kit.front_photo_url : 
                         item.master_kit.front_photo_url.startsWith('uploads/') ? 
                         `${API}/api/${item.master_kit.front_photo_url}` :
                         `${API}/api/uploads/master_kits/${item.master_kit.front_photo_url}.jpg`}
                      alt={`${item.master_kit.club_name || item.master_kit.club || 'Team'} ${item.master_kit.season}`}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-4xl" style={{display: item.master_kit.front_photo_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {item.master_kit.club_name || item.master_kit.club || 'Unknown team'}
                  </h3>
                  <div className="flex items-baseline space-x-2 mb-2">
                    <span className="text-lg font-bold text-gray-900">€{Math.round(item.estimated_price)}</span>
                    <span className="text-xs text-orange-600">Estimate</span>
                  </div>
                  {/* User info with clickable profile */}
                  <div className="text-xs text-gray-500">
                    Owned by{' '}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleUserClick(item.user.id);
                      }}
                      className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                    >
                      {item.user.name}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Latest documentation - Updated to show recent contributions */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
            Latest documentation 📋
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recentContributions.slice(0, 4).map((contrib, index) => {
              const entity = contrib.entity;
              const entityType = contrib.item_type;
              
              return (
                <div
                  key={contrib.contribution_id || index}
                  className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                  onClick={() => onViewChange(entityType === 'team' ? 'teams' : 
                                            entityType === 'brand' ? 'brands' : 
                                            entityType === 'player' ? 'players' : 'competitions')}
                >
                  <div className="flex items-center p-6">
                    <div className="flex-shrink-0 mr-4">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                        {entity.logo_url ? (
                          <img 
                            src={entity.logo_url.startsWith('data:') || entity.logo_url.startsWith('http') 
                              ? entity.logo_url 
                              : entity.logo_url.startsWith('image_uploaded_')
                                ? `${API}/api/legacy-image/${entity.logo_url}`
                                : `${API}/api/${entity.logo_url}`}
                            alt={entity.name || 'Unknown'}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                        ) : null}
                        <span className="text-2xl" style={{display: entity.logo_url ? 'none' : 'flex'}}>
                          {entityType === 'team' ? '⚽' : 
                           entityType === 'brand' ? '👕' : 
                           entityType === 'player' ? '👤' : '🏆'}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-gray-500 mb-1">
                        {contrib.approved_at ? 
                          new Date(contrib.approved_at).toLocaleDateString() : 
                          'Recently'}
                      </div>
                    </div>
                    <div className="flex-2">
                      <h3 className="font-semibold text-gray-900 mb-1">{entity.name || 'Unknown'}</h3>
                      <p className="text-sm text-gray-500 mb-2">
                        New {entityType} documented
                        {contrib.user && (
                          <span> by{' '}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUserClick(contrib.user.id);
                              }}
                              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                            >
                              {contrib.user.name}
                            </button>
                          </span>
                        )}
                      </p>
                      <p className="text-sm font-semibold text-gray-900">
                        <span className="text-green-600">+{contrib.xp_awarded} XP awarded ✓</span>
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Trending brands */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
            Trending brands
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {recentBrands.map((brand) => (
              <div
                key={brand.id}
                className="bg-gray-100 rounded-lg p-6 hover:shadow-md transition-all cursor-pointer group text-center"
                onClick={() => navigate('/catalogue')}
              >
                <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center mx-auto mb-4 shadow-sm overflow-hidden">
                  {brand.logo_url ? (
                    <img 
                      src={brand.logo_url.startsWith('data:') || brand.logo_url.startsWith('http') 
                        ? brand.logo_url 
                        : brand.logo_url.startsWith('image_uploaded_')
                          ? `${process.env.REACT_APP_BACKEND_URL}/api/legacy-image/${brand.logo_url}`
                          : `${process.env.REACT_APP_BACKEND_URL}/api/${brand.logo_url}`}
                      alt={brand.name}
                      className="w-full h-full object-contain p-2"
                      onError={(e) => {
                        console.log('Failed to load brand logo:', e.target.src);
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-2xl" style={{display: brand.logo_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{brand.name}</h3>
                <button className="text-sm text-gray-600 hover:text-black transition-colors">
                  View kits
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Newsletter Section - WhenToCop Style */}
      <div className="py-16 bg-black">
        <div className="max-w-4xl mx-auto px-4 text-center text-white">
          <div className="mb-6">
            <span className="text-4xl">🔥</span>
          </div>
          
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Be the first to know about the latest documentation and exclusive valuations
          </h2>
          <p className="text-lg opacity-90 mb-8">
            Join our newsletter to receive newly documented kits, value estimates and exclusive info from the TopKit community.
          </p>
          
          <div className="flex flex-col sm:flex-row max-w-md mx-auto gap-4">
            <input
              type="email"
              placeholder="Email address"
              className="flex-1 px-4 py-3 rounded-full text-black focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button className="bg-white text-black px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors">
              Subscribe
            </button>
          </div>
          
          <p className="text-sm opacity-70 mt-4">
            By clicking "Subscribe", you accept TopKit's terms and conditions
          </p>
        </div>
      </div>

      {/* Footer Description */}
      <div className="py-8 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Value your football kit collection with TopKit
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            With TopKit, discover the real value of your football kit collection thanks to our collaborative database! 
            Explore the valuations of thousands of kits referenced by the community, from vintage classics to the latest releases. 
            TopKit is the world's most complete collaborative database on football with expert knowledge on every kit. 
            Document your own kits, contribute to valuations and join a passionate community that preserves football history through its kits. 
            Stay informed about new documentation and updated valuations from our expert community.
          </p>
        </div>
      </div>

    </div>
  );
};

export default CollaborativeHomepage;