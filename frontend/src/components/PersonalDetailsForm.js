import React, { useState, useEffect } from 'react';
import { X, Upload, AlertCircle } from 'lucide-react';

const PersonalDetailsForm = ({ 
  isOpen, 
  onClose, 
  onSuccess, 
  masterKit, 
  collectionType = 'owned',
  API 
}) => {
  const [formData, setFormData] = useState({
    name_printing: '',
    number_printing: '',
    patches: '',
    is_signed: false,
    signed_by: '',
    condition: '',
    condition_other: '',
    physical_state: '',
    size: '',
    purchase_price: '',
    purchase_date: '',
    personal_notes: ''
  });

  const [certificateFile, setCertificateFile] = useState(null);
  const [proofOfPurchaseFile, setProofOfPurchaseFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      resetForm();
    }
  }, [isOpen]);

  const resetForm = () => {
    setFormData({
      name_printing: '',
      number_printing: '',
      patches: '',
      is_signed: false,
      signed_by: '',
      condition: '',
      condition_other: '',
      physical_state: '',
      size: '',
      purchase_price: '',
      purchase_date: '',
      personal_notes: ''
    });
    setCertificateFile(null);
    setProofOfPurchaseFile(null);
    setErrors({});
  };

  const handleInputChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Clear error when user starts typing
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
  };

  const handleFileUpload = (event, fileType) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrors(prev => ({
        ...prev,
        [fileType]: 'File must be smaller than 5MB'
      }));
      return;
    }

    if (fileType === 'certificate') {
      setCertificateFile(file);
    } else if (fileType === 'proof_of_purchase') {
      setProofOfPurchaseFile(file);
    }

    // Clear any existing error
    setErrors(prev => ({
      ...prev,
      [fileType]: null
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!masterKit) {
      alert('No Master Kit selected');
      return;
    }

    setIsSubmitting(true);

    try {
      // Upload files first if they exist
      let certificateUrl = null;
      let proofOfPurchaseUrl = null;

      if (certificateFile) {
        const certFormData = new FormData();
        certFormData.append('file', certificateFile);

        const certResponse = await fetch(`${API}/api/upload/certificate`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: certFormData
        });

        if (certResponse.ok) {
          const certResult = await certResponse.json();
          certificateUrl = certResult.file_url;
        }
      }

      if (proofOfPurchaseFile) {
        const proofFormData = new FormData();
        proofFormData.append('file', proofOfPurchaseFile);

        const proofResponse = await fetch(`${API}/api/upload/proof-of-purchase`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: proofFormData
        });

        if (proofResponse.ok) {
          const proofResult = await proofResponse.json();
          proofOfPurchaseUrl = proofResult.file_url;
        }
      }

      // Add to My Collection
      const collectionData = {
        master_kit_id: masterKit.id,
        collection_type: collectionType,
        name_printing: formData.name_printing || null,
        number_printing: formData.number_printing || null,
        patches: formData.patches || null,
        is_signed: formData.is_signed,
        signed_by: formData.is_signed ? (formData.signed_by || null) : null,
        condition: formData.condition || null,
        condition_other: formData.condition === 'other' ? (formData.condition_other || null) : null,
        physical_state: formData.physical_state || null,
        size: formData.size || null,
        purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : null,
        purchase_date: formData.purchase_date || null,
        personal_notes: formData.personal_notes || null
      };

      // Add file URLs if uploaded
      if (certificateUrl) {
        collectionData.certificate_url = certificateUrl;
      }
      if (proofOfPurchaseUrl) {
        collectionData.proof_of_purchase_url = proofOfPurchaseUrl;
      }

      const response = await fetch(`${API}/api/my-collection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(collectionData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add to collection');
      }

      const collectionItem = await response.json();
      
      const successMessage = collectionType === 'owned' 
        ? 'Master Kit added to your collection successfully!' 
        : 'Master Kit added to your want list successfully!';
      
      alert(successMessage);
      onSuccess && onSuccess(collectionItem);
      onClose();

    } catch (error) {
      console.error('Error adding to collection:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen || !masterKit) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">
            Add Personal Details
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isSubmitting}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Master Kit Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900">Adding to My Collection</h3>
                <p className="text-sm text-blue-700 mt-1">
                  {masterKit.club} - {masterKit.season} - {masterKit.kit_type} ({masterKit.brand})
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  All fields are optional. Add as much or as little detail as you want.
                </p>
              </div>
            </div>
          </div>

          {/* Name Printing */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name Printing
            </label>
            <input
              type="text"
              value={formData.name_printing}
              onChange={(e) => handleInputChange('name_printing', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Mbappé, Messi, Your Name"
            />
            <p className="text-xs text-gray-500 mt-1">Name printed on the back of the jersey</p>
          </div>

          {/* Number Printing */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number Printing
            </label>
            <input
              type="text"
              value={formData.number_printing}
              onChange={(e) => handleInputChange('number_printing', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 7, 10, 99"
            />
          </div>

          {/* Patches */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Patches
            </label>
            <select
              value={formData.patches}
              onChange={(e) => handleInputChange('patches', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">No patches</option>
              <option value="ligue_1">Ligue 1</option>
              <option value="champions_league">Champions League</option>
              <option value="europa_league">Europa League</option>
              <option value="premier_league">Premier League</option>
              <option value="la_liga">La Liga</option>
              <option value="serie_a">Serie A</option>
              <option value="bundesliga">Bundesliga</option>
              <option value="world_cup">World Cup</option>
              <option value="euros">European Championship</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Signed Section */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="is_signed"
                checked={formData.is_signed}
                onChange={(e) => handleInputChange('is_signed', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_signed" className="ml-2 block text-sm font-medium text-gray-900">
                This kit is signed
              </label>
            </div>

            {formData.is_signed && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Signed by
                  </label>
                  <input
                    type="text"
                    value={formData.signed_by}
                    onChange={(e) => handleInputChange('signed_by', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="Player name(s) or person who signed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Certificate of Authenticity
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                    {certificateFile ? (
                      <div className="text-center">
                        <p className="text-sm text-gray-900">{certificateFile.name}</p>
                        <button
                          type="button"
                          onClick={() => setCertificateFile(null)}
                          className="mt-2 text-red-600 hover:text-red-800 text-sm"
                        >
                          Remove File
                        </button>
                      </div>
                    ) : (
                      <div className="text-center">
                        <Upload className="mx-auto h-8 w-8 text-gray-400" />
                        <div className="mt-2">
                          <label htmlFor="certificate-file" className="cursor-pointer">
                            <span className="mt-2 block text-sm font-medium text-gray-900">
                              Upload certificate
                            </span>
                            <span className="mt-1 block text-xs text-gray-500">
                              PDF, JPG, PNG up to 5MB
                            </span>
                          </label>
                          <input
                            id="certificate-file"
                            type="file"
                            accept=".pdf,.jpg,.jpeg,.png"
                            onChange={(e) => handleFileUpload(e, 'certificate')}
                            className="hidden"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  {errors.certificate && <p className="text-red-500 text-xs mt-1">{errors.certificate}</p>}
                </div>
              </div>
            )}
          </div>

          {/* Condition */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Condition
            </label>
            <select
              value={formData.condition}
              onChange={(e) => handleInputChange('condition', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select condition</option>
              <option value="club_stock">Club Stock</option>
              <option value="match_prepared">Match Prepared</option>
              <option value="match_worn">Match Worn</option>
              <option value="training">Training</option>
              <option value="other">Other</option>
            </select>
            {formData.condition === 'other' && (
              <input
                type="text"
                value={formData.condition_other}
                onChange={(e) => handleInputChange('condition_other', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 mt-2"
                placeholder="Describe the condition"
              />
            )}
          </div>

          {/* Physical State */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Physical State
            </label>
            <select
              value={formData.physical_state}
              onChange={(e) => handleInputChange('physical_state', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select physical state</option>
              <option value="new_with_tags">New with tags</option>
              <option value="very_good_condition">Very good condition</option>
              <option value="used">Used</option>
              <option value="damaged">Damaged</option>
              <option value="needs_restoration">Needs restoration</option>
            </select>
          </div>

          {/* Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Size
            </label>
            <select
              value={formData.size}
              onChange={(e) => handleInputChange('size', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select size</option>
              <option value="XS">XS</option>
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
              <option value="XL">XL</option>
              <option value="XXL">XXL</option>
              <option value="XXXL">XXXL</option>
            </select>
          </div>

          {/* Purchase Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Purchase Price (€)
            </label>
            <input
              type="number"
              value={formData.purchase_price}
              onChange={(e) => handleInputChange('purchase_price', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="120.00"
              step="0.01"
            />
          </div>

          {/* Purchase Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Purchase Date
            </label>
            <input
              type="date"
              value={formData.purchase_date}
              onChange={(e) => handleInputChange('purchase_date', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Proof of Purchase */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Proof of Purchase
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
              {proofOfPurchaseFile ? (
                <div className="text-center">
                  <p className="text-sm text-gray-900">{proofOfPurchaseFile.name}</p>
                  <button
                    type="button"
                    onClick={() => setProofOfPurchaseFile(null)}
                    className="mt-2 text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove File
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-8 w-8 text-gray-400" />
                  <div className="mt-2">
                    <label htmlFor="proof-file" className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-gray-900">
                        Upload receipt/proof
                      </span>
                      <span className="mt-1 block text-xs text-gray-500">
                        PDF, JPG, PNG up to 5MB
                      </span>
                    </label>
                    <input
                      id="proof-file"
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => handleFileUpload(e, 'proof_of_purchase')}
                      className="hidden"
                    />
                  </div>
                </div>
              )}
            </div>
            {errors.proof_of_purchase && <p className="text-red-500 text-xs mt-1">{errors.proof_of_purchase}</p>}
          </div>

          {/* Personal Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Personal Notes
            </label>
            <textarea
              value={formData.personal_notes}
              onChange={(e) => handleInputChange('personal_notes', e.target.value)}
              rows="3"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="Any additional notes, stories, or details about this kit..."
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Adding...' : 'Add to My Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PersonalDetailsForm;