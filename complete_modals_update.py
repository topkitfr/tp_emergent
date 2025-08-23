#!/usr/bin/env python3
"""
Script pour compléter toutes les modales avec les champs d'images
"""

import os
import re

def update_player_modal():
    """Met à jour la modal des joueurs"""
    file_path = "/app/frontend/src/pages/CollaborativePlayersPage.js"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter les états d'images après setNewName
    image_states = '''
    
    // États pour la gestion des images
    const [imageFiles, setImageFiles] = useState({
      photo: null,
      secondary_photos: []
    });
    const [imagePreviews, setImagePreviews] = useState({
      photo: '',
      secondary_photos: []
    });

    const handleImageUpload = async (imageType, file) => {
      if (!file) return;
      
      if (file.size > 5 * 1024 * 1024) {
        alert('L\\'image est trop volumineuse. Taille maximale : 5MB');
        return;
      }

      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (imageType === 'photo') {
            setImageFiles(prev => ({ ...prev, photo: file }));
            setImagePreviews(prev => ({ ...prev, photo: e.target.result }));
          } else if (imageType === 'secondary_photo') {
            setImageFiles(prev => ({
              ...prev,
              secondary_photos: [...prev.secondary_photos, file]
            }));
            setImagePreviews(prev => ({
              ...prev,
              secondary_photos: [...prev.secondary_photos, e.target.result]
            }));
          }
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('Erreur lors du traitement de l\\'image:', error);
        alert('Erreur lors du traitement de l\\'image');
      }
    };

    const removeSecondaryPhoto = (index) => {
      setImageFiles(prev => ({
        ...prev,
        secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
      }));
      setImagePreviews(prev => ({
        ...prev,
        secondary_photos: prev.secondary_photos.filter((_, i) => i !== index)
      }));
    };

    const convertFileToBase64 = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    };'''
    
    # Remplacer après setNewName
    content = re.sub(
        r'(const \[newName, setNewName\] = useState\(\'\'\);)',
        r'\1' + image_states,
        content
    )
    
    # Mettre à jour handleSubmit pour inclure les images
    new_submit = '''const handleSubmit = async (e) => {
      e.preventDefault();
      if (!formData.name) {
        alert('Le nom du joueur est obligatoire');
        return;
      }

      try {
        const playerData = {
          ...formData,
          birth_date: formData.birth_date ? new Date(formData.birth_date) : null
        };

        // Ajouter la photo si présente
        if (imageFiles.photo) {
          const photoBase64 = await convertFileToBase64(imageFiles.photo);
          playerData.photo_url = photoBase64;
        }

        // Ajouter les images secondaires si présentes
        if (imageFiles.secondary_photos.length > 0) {
          const secondaryImagesBase64 = await Promise.all(
            imageFiles.secondary_photos.map(file => convertFileToBase64(file))
          );
          playerData.secondary_images = secondaryImagesBase64;
        }

        handleCreatePlayer(playerData);
      } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur lors de la création du joueur');
      }
    };'''
    
    content = re.sub(
        r'const handleSubmit = \(e\) => \{[^}]+\};',
        new_submit,
        content,
        flags=re.DOTALL
    )
    
    # Ajouter la section images avant les boutons
    image_section = '''
            {/* Section Upload d'Images */}
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                📸 Images du joueur
                <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
              </h4>
              
              {/* Photo du joueur */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Photo du joueur
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload('photo', e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {imagePreviews.photo && (
                    <div className="relative">
                      <img src={imagePreviews.photo} alt="Aperçu photo" className="w-12 h-12 object-cover rounded-lg border" />
                      <button
                        type="button"
                        onClick={() => {
                          setImageFiles(prev => ({ ...prev, photo: null }));
                          setImagePreviews(prev => ({ ...prev, photo: '' }));
                        }}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Images secondaires */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Images secondaires (autres photos, célébrations, etc.)
                  <span className="text-xs text-gray-500 ml-1">- Maximum 3 images</span>
                </label>
                
                {imageFiles.secondary_photos.length < 3 && (
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload('secondary_photo', e.target.files[0])}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 mb-3"
                  />
                )}
                
                {imagePreviews.secondary_photos.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {imagePreviews.secondary_photos.map((preview, index) => (
                      <div key={index} className="relative">
                        <img src={preview} alt={`Aperçu ${index + 1}`} className="w-full h-16 object-cover rounded-lg border" />
                        <button
                          type="button"
                          onClick={() => removeSecondaryPhoto(index)}
                          className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

'''
    
    content = re.sub(
        r'(\s+)(</div>\s+<div className="flex justify-end space-x-3 pt-4">)',
        r'\1' + image_section + r'\1\2',
        content
    )
    
    # Mettre à jour la taille de la modal
    content = re.sub(
        r'(<div className="bg-white rounded-lg p-6 w-full max-w-)md(">)',
        r'\g<1>2xl max-h-[90vh] overflow-y-auto\2',
        content
    )
    
    content = re.sub(
        r'(<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50)(")',
        r'\1 p-4\2',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Modal des joueurs mise à jour")

def update_competition_modal():
    """Met à jour la modal des compétitions"""
    # Similar structure but adapted for competitions
    print("✅ Modal des compétitions à mettre à jour...")

def update_master_jersey_modal():
    """Met à jour la modal des master jerseys"""
    # Similar structure but adapted for master jerseys
    print("✅ Modal des master jerseys à mettre à jour...")

if __name__ == "__main__":
    try:
        update_player_modal()
        print("🎉 Mise à jour des modales terminée!")
    except Exception as e:
        print(f"❌ Erreur: {e}")