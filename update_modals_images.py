#!/usr/bin/env python3
"""
Script pour ajouter les champs d'upload d'images aux modales d'ajout
"""

import re

def add_image_section_to_modal(file_path, entity_type):
    """Ajoute la section d'upload d'images à une modal"""
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trouver le pattern de fin avant les boutons de validation
    # Chercher la div avec les boutons Annuler/Créer
    pattern = r'(\s*)(</div>\s*<div className="flex justify-end space-x-3 pt-4">)'
    
    # Définir le contenu d'upload d'images selon le type d'entité
    if entity_type == 'brand':
        image_label = "Logo de la marque"
        secondary_label = "Images secondaires (évolution du logo, etc.)"
    elif entity_type == 'player':
        image_label = "Photo du joueur"
        secondary_label = "Images secondaires (autres photos, etc.)"
    elif entity_type == 'competition':
        image_label = "Logo de la compétition"
        secondary_label = "Images secondaires (logos historiques, etc.)"
    elif entity_type == 'jersey':
        image_label = "Photo principale du maillot"
        secondary_label = "Photos supplémentaires (détails, dos, etc.)"
    else:  # team
        image_label = "Logo de l'équipe"
        secondary_label = "Images secondaires (anciens logos, photos, etc.)"
    
    # Contenu de la section d'images
    image_section = f'''

            {{/* Section Upload d'Images */}}
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                📸 Images {f"de l'{entity_type}" if entity_type in ['équipe'] else f"de la {entity_type}" if entity_type in ['marque', 'compétition'] else f"du {entity_type}"}
                <span className="text-xs text-gray-500 font-normal">(optionnel, max 5MB par image)</span>
              </h4>
              
              {{/* Logo/Photo principale */}}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {image_label}
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={{(e) => handleImageUpload('logo', e.target.files[0])}}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {{imagePreviews.logo && (
                    <div className="relative">
                      <img src={{imagePreviews.logo}} alt="Aperçu" className="w-12 h-12 object-cover rounded-lg border" />
                      <button
                        type="button"
                        onClick={{() => {{
                          setImageFiles(prev => ({{ ...prev, logo: null }}));
                          setImagePreviews(prev => ({{ ...prev, logo: '' }}));
                        }}}}
                        className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  )}}
                </div>
              </div>

              {{/* Images secondaires */}}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {secondary_label}
                  <span className="text-xs text-gray-500 ml-1">- Maximum 3 images</span>
                </label>
                
                {{imageFiles.secondary_photos.length < 3 && (
                  <input
                    type="file"
                    accept="image/*"
                    onChange={{(e) => handleImageUpload('secondary_photo', e.target.files[0])}}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 mb-3"
                  />
                )}}
                
                {{imagePreviews.secondary_photos.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {{imagePreviews.secondary_photos.map((preview, index) => (
                      <div key={{index}} className="relative">
                        <img src={{preview}} alt={{`Aperçu ${{index + 1}}`}} className="w-full h-16 object-cover rounded-lg border" />
                        <button
                          type="button"
                          onClick={{() => removeSecondaryPhoto(index)}}
                          className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs hover:bg-red-600"
                        >
                          ×
                        </button>
                      </div>
                    ))}}
                  </div>
                )}}
              </div>
            </div>'''
    
    # Remplacer le pattern trouvé
    replacement = r'\1' + image_section + r'\1\2'
    new_content = re.sub(pattern, replacement, content)
    
    # Également mettre à jour la taille de la modal
    new_content = re.sub(
        r'(<div className="bg-white rounded-lg p-6 w-full max-w-)md(">)',
        r'\g<1>2xl max-h-[90vh] overflow-y-auto\2',
        new_content
    )
    
    # Mettre à jour le conteneur de la modal pour le padding
    new_content = re.sub(
        r'(<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50)(")',
        r'\1 p-4\2',
        new_content
    )
    
    # Écrire le fichier mis à jour
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {file_path} mis à jour avec les champs d'images")

if __name__ == "__main__":
    # Définir les fichiers à modifier
    modals_to_update = [
        ("/app/frontend/src/pages/CollaborativeBrandsPage.js", "marque"),
        ("/app/frontend/src/pages/CollaborativePlayersPage.js", "joueur"),
        ("/app/frontend/src/pages/CollaborativeCompetitionsPage.js", "compétition"),
        ("/app/frontend/src/pages/CollaborativeMasterJerseyPage.js", "maillot")
    ]
    
    for file_path, entity_type in modals_to_update:
        try:
            add_image_section_to_modal(file_path, entity_type)
        except Exception as e:
            print(f"❌ Erreur pour {file_path}: {e}")
    
    print("🎉 Toutes les modales ont été mises à jour!")