import React from 'react';

const CollaborativeHomepage = ({ user, teams, brands, players, masterJerseys, onViewChange }) => {
  
  // Statistics
  const stats = [
    { label: 'Teams', value: teams?.length || 0, icon: '⚽', color: 'text-gray-900' },
    { label: 'Brands', value: brands?.length || 0, icon: '👕', color: 'text-gray-900' },
    { label: 'Players', value: players?.length || 0, icon: '👤', color: 'text-gray-900' },
    { label: 'Kits', value: masterJerseys?.length || 0, icon: '📋', color: 'text-gray-900' }
  ];

  const recentTeams = teams?.slice(0, 6) || [];
  const recentBrands = brands?.slice(0, 4) || [];
  const recentMasterJerseys = masterJerseys?.slice(0, 12) || [];

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section - TopKit Narrative with Background Banner */}
      <div 
        className="bg-white py-16 md:py-24 relative bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url('https://customer-assets.emergentagent.com/job_footwear-collab/artifacts/3cir86pr_EmzagksXIAg35Ia.jpg')`
        }}
      >
        <div className="max-w-6xl mx-auto px-4 text-center relative z-10">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Value your collection <br />
            <span className="text-gray-600">of football kits</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Discover the value of your kits with TopKit, 
            the world's most complete collaborative database on football
          </p>
          
          {/* CTA Buttons - TopKit Focus - Removed Documenter button */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={() => onViewChange('vestiaire')}
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
                onClick={() => onViewChange('catalogue')}
                className="flex-shrink-0 bg-white rounded-lg p-4 hover:shadow-md transition-all border border-gray-100 min-w-[120px]"
              >
                <div className="text-center">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2 overflow-hidden">
                    {team.logo_url ? (
                      <img 
                        src={team.logo_url.startsWith('data:') || team.logo_url.startsWith('http') ? team.logo_url : `/api/${team.logo_url}`}
                        alt={team.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <span className="text-xl" style={{display: team.logo_url ? 'none' : 'flex'}}>⚽</span>
                  </div>
                  <div className="font-medium text-sm text-gray-900 truncate">{team.name}</div>
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
              onClick={() => onViewChange('master-jerseys')}
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
                onClick={() => onViewChange('master-jerseys')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                  {jersey.main_image_url ? (
                    <img 
                      src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `/api/${jersey.main_image_url}`}
                      alt={`${jersey.team_info?.name || 'Team'} ${jersey.season}`}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-4xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {jersey.team_info?.name || 'Unknown team'}
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

      {/* Latest contributions Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              Latest database contributions 🔥
            </h2>
            <button
              onClick={() => onViewChange('teams')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              View contributions
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recentTeams.slice(0, 2).map((team, index) => (
              <div
                key={team.id}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group"
                onClick={() => onViewChange('teams')}
              >
                <div className="flex items-center p-6">
                  <div className="flex-shrink-0 mr-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                      {team.logo_url ? (
                        <img 
                          src={team.logo_url.startsWith('data:') || team.logo_url.startsWith('http') ? team.logo_url : `/api/${team.logo_url}`}
                          alt={team.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <span className="text-2xl" style={{display: team.logo_url ? 'none' : 'flex'}}>⚽</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm text-gray-500 mb-1">
                      Jan
                      <br />
                      {15 + index}
                    </div>
                  </div>
                  <div className="flex-2">
                    <h3 className="font-semibold text-gray-900 mb-1">{team.name}</h3>
                    <p className="text-sm text-gray-500 mb-2">New team documented</p>
                    <p className="text-sm font-semibold text-gray-900">
                      <span className="text-green-600">+5 kits referenced</span>
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Rare and sought-after kits */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Rare and sought-after kits</h2>
            <button
              onClick={() => onViewChange('master-jerseys')}
              className="text-gray-600 hover:text-black transition-colors text-sm font-medium"
            >
              View more rare kits
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.slice(0, 6).map((jersey, index) => {
              const rareValues = [450, 680, 1200, 350, 890, 750];
              const rareValue = rareValues[index % 6];
              
              return (
                <div
                  key={jersey.id || index}
                  className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100 relative"
                  onClick={() => onViewChange('master-jerseys')}
                >
                  <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-bold">
                    RARE
                  </div>
                  <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                    {jersey.main_image_url ? (
                      <img 
                        src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `/api/${jersey.main_image_url}`}
                        alt={`${jersey.team_info?.name || 'Team'} ${jersey.season}`}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <span className="text-4xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                      {jersey.team_info?.name || 'Unknown team'}
                    </h3>
                    <div className="flex items-baseline space-x-2">
                      <span className="text-lg font-bold text-gray-900">{rareValue}€</span>
                      <span className="text-xs text-orange-600">Estimate</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Latest documentation */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
            Latest documentation 📋
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recentMasterJerseys.slice(0, 6).map((jersey, index) => (
              <div
                key={jersey.id || index}
                className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer group border border-gray-100"
                onClick={() => onViewChange('master-jerseys')}
              >
                <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                  {jersey.main_image_url ? (
                    <img 
                      src={jersey.main_image_url.startsWith('data:') || jersey.main_image_url.startsWith('http') ? jersey.main_image_url : `/api/${jersey.main_image_url}`}
                      alt={`${jersey.team_info?.name || 'Team'} ${jersey.season}`}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-4xl" style={{display: jersey.main_image_url ? 'none' : 'flex'}}>👕</span>
                </div>
                <div className="p-3">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                    {jersey.team_info?.name || 'Unknown team'} {jersey.season}
                  </h3>
                  <p className="text-sm text-green-600">
                    <span className="text-lg font-bold">Documented ✓</span>
                  </p>
                </div>
              </div>
            ))}
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
                onClick={() => onViewChange('brands')}
              >
                <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center mx-auto mb-4 shadow-sm overflow-hidden">
                  {brand.logo_url ? (
                    <img 
                      src={brand.logo_url.startsWith('data:') || brand.logo_url.startsWith('http') ? brand.logo_url : `/api/${brand.logo_url}`}
                      alt={brand.name}
                      className="w-full h-full object-contain p-2"
                      onError={(e) => {
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