import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, Check, X, MessageSquare, Star } from 'lucide-react';

const FieldSpecificVoting = ({ contribution, currentUser, onVote, className = '' }) => {
  const [fieldVotes, setFieldVotes] = useState({});
  const [showAdvancedVoting, setShowAdvancedVoting] = useState(false);
  const [comment, setComment] = useState('');
  const [overallVote, setOverallVote] = useState(null);
  
  // Define which fields are voteable for each entity type
  const getVoteableFields = (entityType, data) => {
    const baseFields = [];
    
    switch (entityType) {
      case 'team':
        return [
          { key: 'name', label: 'Team Name', value: data.name },
          { key: 'country', label: 'Country', value: data.country },
          { key: 'city', label: 'City', value: data.city },
          { key: 'founded_year', label: 'Founded Year', value: data.founded_year },
          { key: 'colors', label: 'Team Colors', value: Array.isArray(data.colors) ? data.colors.join(', ') : data.colors }
        ];
      
      case 'brand':
        return [
          { key: 'name', label: 'Brand Name', value: data.name },
          { key: 'country', label: 'Country', value: data.country },
          { key: 'founded_year', label: 'Founded Year', value: data.founded_year },
          { key: 'website', label: 'Website', value: data.website }
        ];
      
      case 'player':
        return [
          { key: 'name', label: 'Player Name', value: data.name },
          { key: 'nationality', label: 'Nationality', value: data.nationality },
          { key: 'birth_date', label: 'Birth Date', value: data.birth_date },
          { key: 'position', label: 'Position', value: data.position },
          { key: 'current_team', label: 'Current Team', value: data.current_team }
        ];
      
      case 'competition':
        return [
          { key: 'competition_name', label: 'Competition Name', value: data.competition_name },
          { key: 'competition_type', label: 'Type', value: data.competition_type },
          { key: 'country', label: 'Country', value: data.country },
          { key: 'federation', label: 'Federation', value: data.federation }
        ];
      
      case 'master_kit':
        return [
          { key: 'season', label: 'Season', value: data.season },
          { key: 'jersey_type', label: 'Kit Type', value: data.jersey_type },
          { key: 'primary_color', label: 'Primary Color', value: data.primary_color },
          { key: 'secondary_colors', label: 'Secondary Colors', value: data.secondary_colors },
          { key: 'main_sponsor', label: 'Main Sponsor', value: data.main_sponsor }
        ];
      
      case 'reference_kit':
        return [
          { key: 'model_name', label: 'Model Name', value: data.model_name },
          { key: 'release_type', label: 'Release Type', value: data.release_type },
          { key: 'original_retail_price', label: 'Original Price', value: data.original_retail_price },
          { key: 'release_date', label: 'Release Date', value: data.release_date }
        ];
      
      default:
        return [];
    }
  };

  const voteableFields = getVoteableFields(contribution.entity_type, contribution.data);

  const handleFieldVote = (fieldKey, voteType) => {
    setFieldVotes(prev => ({
      ...prev,
      [fieldKey]: voteType
    }));
  };

  const handleSubmitVote = async () => {
    try {
      await onVote(contribution.id, {
        vote_type: overallVote,
        comment: comment,
        field_votes: fieldVotes
      });
      
      // Reset form
      setFieldVotes({});
      setComment('');
      setOverallVote(null);
      setShowAdvancedVoting(false);
      
    } catch (error) {
      console.error('Error submitting vote:', error);
      alert('Error submitting vote. Please try again.');
    }
  };

  const getFieldVoteStats = (fieldKey) => {
    // In a real implementation, this would come from the contribution data
    // For now, we'll simulate vote statistics
    const votes = contribution.votes || [];
    let upvotes = 0;
    let downvotes = 0;
    
    votes.forEach(vote => {
      if (vote.field_votes && vote.field_votes[fieldKey]) {
        if (vote.field_votes[fieldKey] === 'upvote') upvotes++;
        else if (vote.field_votes[fieldKey] === 'downvote') downvotes++;
      }
    });
    
    return { upvotes, downvotes };
  };

  const getFieldAccuracy = (fieldKey) => {
    const stats = getFieldVoteStats(fieldKey);
    const total = stats.upvotes + stats.downvotes;
    if (total === 0) return null;
    return Math.round((stats.upvotes / total) * 100);
  };

  if (!contribution.user_can_vote) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <p className="text-sm text-gray-600 text-center">
          You cannot vote on your own contribution
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-gray-900">Community Voting</h3>
        
        {/* Overall Vote Buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setOverallVote('upvote')}
            className={`flex items-center gap-1 px-3 py-2 rounded-lg transition-colors ${
              overallVote === 'upvote' 
                ? 'bg-green-600 text-white' 
                : 'bg-green-50 text-green-700 hover:bg-green-100'
            }`}
          >
            <ThumbsUp className="w-4 h-4" />
            {contribution.upvotes}
          </button>
          <button
            onClick={() => setOverallVote('downvote')}
            className={`flex items-center gap-1 px-3 py-2 rounded-lg transition-colors ${
              overallVote === 'downvote' 
                ? 'bg-red-600 text-white' 
                : 'bg-red-50 text-red-700 hover:bg-red-100'
            }`}
          >
            <ThumbsDown className="w-4 h-4" />
            {contribution.downvotes}
          </button>
        </div>
      </div>

      {/* Advanced Voting Toggle */}
      <div className="mb-4">
        <button
          onClick={() => setShowAdvancedVoting(!showAdvancedVoting)}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
        >
          <Star className="w-4 h-4" />
          {showAdvancedVoting ? 'Hide' : 'Show'} Field-Specific Voting
        </button>
      </div>

      {/* Field-Specific Voting */}
      {showAdvancedVoting && (
        <div className="space-y-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800">
              <strong>Field-Specific Voting:</strong> Vote on individual fields to provide more detailed feedback.
              This helps improve data quality and gives contributors specific guidance.
            </p>
          </div>
          
          <div className="grid grid-cols-1 gap-3">
            {voteableFields.map(field => {
              const stats = getFieldVoteStats(field.key);
              const accuracy = getFieldAccuracy(field.key);
              
              return (
                <div key={field.key} className="bg-gray-50 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 text-sm">{field.label}</p>
                      <p className="text-gray-700 text-sm">{field.value || 'Not provided'}</p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {accuracy !== null && (
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          accuracy >= 80 ? 'bg-green-100 text-green-800' :
                          accuracy >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {accuracy}% accurate
                        </span>
                      )}
                      
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleFieldVote(field.key, 'upvote')}
                          className={`p-1 rounded transition-colors ${
                            fieldVotes[field.key] === 'upvote'
                              ? 'bg-green-600 text-white'
                              : 'bg-green-100 text-green-600 hover:bg-green-200'
                          }`}
                        >
                          <Check className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => handleFieldVote(field.key, 'downvote')}
                          className={`p-1 rounded transition-colors ${
                            fieldVotes[field.key] === 'downvote'
                              ? 'bg-red-600 text-white'
                              : 'bg-red-100 text-red-600 hover:bg-red-200'
                          }`}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Field Vote Stats */}
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Check className="w-3 h-3 text-green-600" />
                      {stats.upvotes} correct
                    </span>
                    <span className="flex items-center gap-1">
                      <X className="w-3 h-3 text-red-600" />
                      {stats.downvotes} incorrect
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Comment Section */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <MessageSquare className="w-4 h-4 inline mr-1" />
          Comment (Optional)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Provide feedback to help improve this contribution..."
          rows={3}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Submit Button */}
      <div className="flex justify-between items-center">
        <div className="text-xs text-gray-500">
          {Object.keys(fieldVotes).length > 0 && (
            <span>{Object.keys(fieldVotes).length} field votes selected</span>
          )}
        </div>
        
        <button
          onClick={handleSubmitVote}
          disabled={!overallVote}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          Submit Vote
          {showAdvancedVoting && Object.keys(fieldVotes).length > 0 && (
            <span className="bg-blue-500 text-xs px-2 py-1 rounded-full">
              +{Object.keys(fieldVotes).length}
            </span>
          )}
        </button>
      </div>

      {/* Voting Rules Reminder */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>3 upvotes = auto-approve</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span>2 downvotes = auto-reject</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>Field votes improve accuracy</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FieldSpecificVoting;