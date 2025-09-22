import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import GamificationProfile from '../components/GamificationProfile';
import SocialFeatures from '../components/SocialFeatures';
import CollectionStats from '../components/CollectionStats';
import UserActivityFeed from '../components/UserActivityFeed';

const PublicProfilePage = ({ user, API }) => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    if (!user) {
      navigate('/');
      return;
    }

    // Don't allow viewing own profile here (redirect to regular profile page)
    if (user.id === userId) {
      navigate('/profile');
      return;
    }

    loadPublicProfile();
  }, [userId, user]);

  const loadPublicProfile = async () => {
    if (!user?.token) {
      setError('Authentication required');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API}/api/users/${userId}/public-profile`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProfileData(data);
      } else if (response.status === 404) {
        setError('User not found');
      } else if (response.status === 403) {
        setError('This profile is private');
      } else {
        setError('Failed to load profile');
      }
    } catch (error) {
      console.error('Error loading public profile:', error);
      setError('Error loading profile');
    }
    
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Profile Unavailable</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            Go Back Home
          </button>
        </div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Profile Not Found</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            Go Back Home
          </button>
        </div>
      </div>
    );
  }

  const memberSinceDate = profileData.created_at ? 
    new Date(profileData.created_at).toLocaleDateString() : 'Unknown';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center mb-4">
            <button
              onClick={() => navigate(-1)}
              className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{profileData.name}'s Profile</h1>
              <p className="text-gray-600">View contributor profile and achievements</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* User Info Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start space-x-4">
              {/* Profile Picture */}
              <div className="flex-shrink-0">
                {profileData.profile_picture_url ? (
                  <img 
                    src={`${API}/${profileData.profile_picture_url}`}
                    alt="Profile"
                    className="w-20 h-20 rounded-full object-cover border-2 border-gray-200"
                  />
                ) : (
                  <div className="w-20 h-20 bg-gray-300 rounded-full flex items-center justify-center text-2xl font-bold text-gray-600">
                    {profileData.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                )}
              </div>
              
              {/* User Details */}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{profileData.name}</h2>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mt-2">
                      <span>Member since {memberSinceDate}</span>
                      {profileData.role === 'admin' && (
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                          Admin
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Bio */}
                {profileData.bio && (
                  <div className="mt-4">
                    <p className="text-gray-700">{profileData.bio}</p>
                  </div>
                )}

                {/* Social Links */}
                <div className="mt-4 flex flex-wrap gap-3">
                  {profileData.favorite_club && (
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="mr-1">⚽</span>
                      <span>{profileData.favorite_club}</span>
                    </div>
                  )}
                  {profileData.instagram_username && (
                    <a 
                      href={`https://instagram.com/${profileData.instagram_username.replace('@', '')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                    >
                      <span className="mr-1">📷</span>
                      <span>@{profileData.instagram_username.replace('@', '')}</span>
                    </a>
                  )}
                  {profileData.twitter_username && (
                    <a 
                      href={`https://twitter.com/${profileData.twitter_username.replace('@', '')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                    >
                      <span className="mr-1">🐦</span>
                      <span>@{profileData.twitter_username.replace('@', '')}</span>
                    </a>
                  )}
                  {profileData.website && (
                    <a 
                      href={profileData.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                    >
                      <span className="mr-1">🌐</span>
                      <span>Website</span>
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {profileData.collections_count || 0}
              </div>
              <div className="text-sm text-gray-600">Collections</div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {profileData.contributions_count || 0}
              </div>
              <div className="text-sm text-gray-600">Contributions</div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {profileData.xp || 0}
              </div>
              <div className="text-sm text-gray-600">Total XP</div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {profileData.level || 'Remplaçant'}
              </div>
              <div className="text-sm text-gray-600">Level</div>
            </div>
          </div>

          {/* Gamification Profile */}
          <GamificationProfile 
            user={{ id: profileData.id, token: user.token }} 
            API={API} 
          />

          {/* Note about limited profile access */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Limited Profile View</h3>
                <p className="text-sm text-blue-700 mt-1">
                  You're viewing a public profile. Some information may be limited based on the user's privacy settings.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicProfilePage;