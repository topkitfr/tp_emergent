import React, { useState, useRef, useCallback } from 'react';
import { uploadImage } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { Upload, X, Image, Link2, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ImageUpload({ value, onChange, label, testId }) {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [mode, setMode] = useState('upload'); // 'upload' or 'url'
  const [urlInput, setUrlInput] = useState('');
  const fileRef = useRef(null);

  const resolveUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('/api/uploads/')) return `${BACKEND_URL}${url}`;
    return url;
  };

  const handleFile = useCallback(async (file) => {
    if (!file) return;
    const valid = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!valid.includes(file.type)) {
      toast.error('Only JPG, PNG, WebP, or GIF allowed');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File too large (max 10MB)');
      return;
    }
    setUploading(true);
    try {
      const res = await uploadImage(file);
      onChange(res.data.url);
      toast.success('Image uploaded');
    } catch (err) {
      toast.error('Upload failed');
      console.error(err);
    } finally {
      setUploading(false);
    }
  }, [onChange]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleUrlSubmit = () => {
    if (urlInput.trim()) {
      onChange(urlInput.trim());
      setUrlInput('');
    }
  };

  const handleClear = () => {
    onChange('');
    if (fileRef.current) fileRef.current.value = '';
  };

  const displayUrl = resolveUrl(value);

  return (
    <div className="space-y-2" data-testid={testId || 'image-upload'}>
      {/* Mode Toggle */}
      <div className="flex items-center gap-1 mb-1">
        <button
          type="button"
          onClick={() => setMode('upload')}
          className={`flex items-center gap-1 px-2 py-1 text-[10px] uppercase tracking-wider border ${mode === 'upload' ? 'border-primary text-primary bg-primary/5' : 'border-border text-muted-foreground hover:text-foreground'}`}
          style={{ fontFamily: 'Barlow Condensed, sans-serif', transition: 'border-color 0.2s, color 0.2s' }}
          data-testid={`${testId || 'image-upload'}-tab-upload`}
        >
          <Upload className="w-3 h-3" /> Upload
        </button>
        <button
          type="button"
          onClick={() => setMode('url')}
          className={`flex items-center gap-1 px-2 py-1 text-[10px] uppercase tracking-wider border ${mode === 'url' ? 'border-primary text-primary bg-primary/5' : 'border-border text-muted-foreground hover:text-foreground'}`}
          style={{ fontFamily: 'Barlow Condensed, sans-serif', transition: 'border-color 0.2s, color 0.2s' }}
          data-testid={`${testId || 'image-upload'}-tab-url`}
        >
          <Link2 className="w-3 h-3" /> URL
        </button>
      </div>

      {mode === 'upload' ? (
        /* Drop Zone */
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !uploading && fileRef.current?.click()}
          className={`relative border-2 border-dashed cursor-pointer group overflow-hidden
            ${dragOver ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/40'}
            ${value ? 'p-0' : 'p-6'}
          `}
          style={{ transition: 'border-color 0.2s, background-color 0.2s' }}
          data-testid={`${testId || 'image-upload'}-dropzone`}
        >
          {value ? (
            <div className="relative aspect-[4/3]">
              <img
                src={displayUrl}
                alt="Uploaded"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center gap-2" style={{ transition: 'opacity 0.2s' }}>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}
                  className="p-2 bg-card border border-border text-foreground hover:bg-primary hover:text-primary-foreground"
                  style={{ transition: 'background-color 0.2s' }}
                  data-testid={`${testId || 'image-upload'}-replace`}
                >
                  <Upload className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); handleClear(); }}
                  className="p-2 bg-card border border-border text-foreground hover:bg-destructive hover:text-destructive-foreground"
                  style={{ transition: 'background-color 0.2s' }}
                  data-testid={`${testId || 'image-upload'}-clear`}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : uploading ? (
            <div className="flex flex-col items-center justify-center py-4">
              <Loader2 className="w-6 h-6 text-primary animate-spin mb-2" />
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Uploading...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-10 h-10 border border-border flex items-center justify-center mb-3 group-hover:border-primary/40" style={{ transition: 'border-color 0.2s' }}>
                <Image className="w-5 h-5 text-muted-foreground group-hover:text-primary" style={{ transition: 'color 0.2s' }} />
              </div>
              <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                <span className="text-foreground font-medium">Click to upload</span> or drag and drop
              </p>
              <p className="text-[10px] text-muted-foreground mt-1" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                JPG, PNG, WebP, GIF -- max 10MB
              </p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
            data-testid={`${testId || 'image-upload'}-file-input`}
          />
        </div>
      ) : (
        /* URL Input */
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/jersey.jpg"
              className="bg-card border-border rounded-none flex-1"
              onKeyDown={(e) => e.key === 'Enter' && handleUrlSubmit()}
              data-testid={`${testId || 'image-upload'}-url-input`}
            />
            <Button
              type="button"
              onClick={handleUrlSubmit}
              disabled={!urlInput.trim()}
              className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0"
              data-testid={`${testId || 'image-upload'}-url-submit`}
            >
              Set
            </Button>
          </div>
          {value && (
            <div className="relative aspect-[4/3] border border-border overflow-hidden group">
              <img src={displayUrl} alt="Preview" className="w-full h-full object-cover" />
              <button
                type="button"
                onClick={handleClear}
                className="absolute top-2 right-2 p-1 bg-card/80 border border-border text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100"
                style={{ transition: 'opacity 0.2s' }}
                data-testid={`${testId || 'image-upload'}-url-clear`}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
