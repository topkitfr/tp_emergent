import React, { useState, useEffect } from 'react';

const ProfileCompleteness = ({ user, API, onFieldClick }) => {
  const [completenessData, setCompletenessData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchCompletenessData();
    }
  }, [user]);

  const fetchCompletenessData = async () => {
    try {
      const response = await fetch(`${API}/api/users/${user.id}/profile-completeness`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCompletenessData(data);
      }
    } catch (error) {
      console.error('Error fetching profile completeness:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !completenessData) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-2 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    );
  }

  const { completeness_percentage, suggestions, missing_required, missing_optional } = completenessData;
  
  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-blue-500';
    if (percentage >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getProgressMessage = (percentage) => {
    if (percentage === 100) return 'Your profile is complete! 🎉';
    if (percentage >= 80) return 'Almost there! Just a few more details.';
    if (percentage >= 60) return 'Good progress! Keep adding details.';
    if (percentage >= 40) return 'You\'re getting started! Add more info.';
    return 'Let\'s build your profile!';
  };

  const fieldLabels = {
    bio: 'Bio',
    favorite_club: 'Favorite Club',
    profile_picture_url: 'Profile Picture',
    instagram_username: 'Instagram',
    twitter_username: 'Twitter',
    website: 'Website'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Profile Completeness</h3>
        <div className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-gray-900">{completeness_percentage}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-600">
            {getProgressMessage(completeness_percentage)}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(completeness_percentage)}`}
            style={{ width: `${completeness_percentage}%` }}
          ></div>
        </div>
      </div>

      {/* Missing Required Fields */}
      {missing_required.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <span className="mr-2">⚠️</span>Missing Required Fields
          </h4>
          <div className="flex flex-wrap gap-2">
            {missing_required.map((field) => (
              <button
                key={field}
                onClick={() => onFieldClick && onFieldClick(field)}
                className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium hover:bg-red-200 transition-colors cursor-pointer"
              >
                {fieldLabels[field] || field}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Missing Optional Fields */}
      {missing_optional.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <span className="mr-2">💡</span>Optional Enhancements
          </h4>
          <div className="flex flex-wrap gap-2">
            {missing_optional.map((field) => (
              <button
                key={field}
                onClick={() => onFieldClick && onFieldClick(field)}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium hover:bg-blue-200 transition-colors cursor-pointer"
              >
                {fieldLabels[field] || field}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="border-t border-gray-200 pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">💪 Quick Wins</h4>
          <ul className="space-y-1 text-sm text-gray-600">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="mr-2 text-green-500">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ProfileCompleteness;