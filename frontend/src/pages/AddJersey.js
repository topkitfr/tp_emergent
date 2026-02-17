import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createMasterKit, createVersion, getMasterKits } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Shirt, ArrowRight, ArrowLeft, Check, Plus } from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special'];
const MODELS = ['Replica', 'Authentic', 'Player Issue'];
const GENDERS = ['Men', 'Women', 'Kids'];

export default function AddJersey() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1 = Master Kit, 2 = Version
  const [existingKits, setExistingKits] = useState([]);
  const [selectedExistingKit, setSelectedExistingKit] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Master Kit fields
  const [club, setClub] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());

  // Version fields
  const [competition, setCompetition] = useState('');
  const [model, setModel] = useState('');
  const [gender, setGender] = useState('');
  const [skuCode, setSkuCode] = useState('');
  const [verFrontPhoto, setVerFrontPhoto] = useState('');
  const [verBackPhoto, setVerBackPhoto] = useState('');

  const [createdKitId, setCreatedKitId] = useState('');

  useEffect(() => {
    getMasterKits({}).then(r => setExistingKits(r.data)).catch(() => {});
  }, []);

  const handleCreateKit = async () => {
    if (!club || !season || !kitType || !brand || !frontPhoto) {
      toast.error('Please fill all required fields');
      return;
    }
    setSubmitting(true);
    try {
      const res = await createMasterKit({ club, season, kit_type: kitType, brand, front_photo: frontPhoto, year: parseInt(year) });
      setCreatedKitId(res.data.kit_id);
      toast.success('Master Kit created');
      setStep(2);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create kit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateVersion = async () => {
    const kitId = createdKitId || selectedExistingKit;
    if (!kitId) { toast.error('Please select or create a Master Kit first'); return; }
    if (!competition || !model || !gender) { toast.error('Please fill required fields'); return; }
    setSubmitting(true);
    try {
      const res = await createVersion({
        kit_id: kitId, competition, model, gender,
        sku_code: skuCode, front_photo: verFrontPhoto, back_photo: verBackPhoto
      });
      toast.success('Version created');
      navigate(`/version/${res.data.version_id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create version');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="add-jersey-title">
            ADD JERSEY
          </h1>
          <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
            Contribute to the catalog by adding new kits and versions
          </p>
          {/* Steps */}
          <div className="flex items-center gap-4 mt-6">
            <div className={`flex items-center gap-2 ${step === 1 ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${step === 1 ? 'bg-primary text-primary-foreground' : step > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                {step > 1 ? <Check className="w-3 h-3" /> : '1'}
              </div>
              <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>MASTER KIT</span>
            </div>
            <div className="w-8 h-px bg-border" />
            <div className={`flex items-center gap-2 ${step === 2 ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${step === 2 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'}`}>
                2
              </div>
              <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>VERSION</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 lg:px-8 py-8">
        {step === 1 && (
          <div className="space-y-6" data-testid="step-1-form">
            <div className="border border-border p-6 mb-6">
              <h3 className="text-sm mb-4" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>USE EXISTING KIT</h3>
              <Select value={selectedExistingKit} onValueChange={(v) => { setSelectedExistingKit(v); }}>
                <SelectTrigger className="bg-card border-border rounded-none" data-testid="select-existing-kit">
                  <SelectValue placeholder="Select an existing Master Kit" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border max-h-60">
                  {existingKits.map(k => (
                    <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedExistingKit && (
                <Button onClick={() => setStep(2)} className="mt-3 rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="use-existing-kit-btn">
                  Continue with this Kit <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </div>

            <div className="text-center text-xs text-muted-foreground tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>
              OR CREATE NEW
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Club / Team *</Label>
                <Input value={club} onChange={e => setClub(e.target.value)} placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" data-testid="input-club" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Season *</Label>
                <Input value={season} onChange={e => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" data-testid="input-season" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Type *</Label>
                <Select value={kitType} onValueChange={setKitType}>
                  <SelectTrigger className="bg-card border-border rounded-none" data-testid="select-kit-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Brand *</Label>
                <Input value={brand} onChange={e => setBrand(e.target.value)} placeholder="e.g., Nike" className="bg-card border-border rounded-none" data-testid="input-brand" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Year *</Label>
                <Input type="number" value={year} onChange={e => setYear(e.target.value)} className="bg-card border-border rounded-none" data-testid="input-year" />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Front Photo *</Label>
                <ImageUpload value={frontPhoto} onChange={setFrontPhoto} label="Front Photo" testId="upload-front-photo" />
              </div>
            </div>

            <Button onClick={handleCreateKit} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="create-kit-btn">
              {submitting ? 'Creating...' : 'Create Master Kit'} <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6" data-testid="step-2-form">
            <div className="flex items-center gap-2 mb-4">
              <button onClick={() => setStep(1)} className="text-muted-foreground hover:text-foreground" data-testid="back-to-step-1">
                <ArrowLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>
                ADDING VERSION {createdKitId ? 'TO NEW KIT' : `TO ${existingKits.find(k => k.kit_id === selectedExistingKit)?.club || 'SELECTED KIT'}`}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Competition *</Label>
                <Input value={competition} onChange={e => setCompetition(e.target.value)} placeholder="e.g., Champions League 2024/2025" className="bg-card border-border rounded-none" data-testid="input-competition" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Model *</Label>
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger className="bg-card border-border rounded-none" data-testid="select-model">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Gender *</Label>
                <Select value={gender} onValueChange={setGender}>
                  <SelectTrigger className="bg-card border-border rounded-none" data-testid="select-gender">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>SKU Code</Label>
                <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" data-testid="input-sku" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Front Photo URL</Label>
                <Input value={verFrontPhoto} onChange={e => setVerFrontPhoto(e.target.value)} placeholder="https://..." className="bg-card border-border rounded-none" data-testid="input-ver-front-photo" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Back Photo URL</Label>
                <Input value={verBackPhoto} onChange={e => setVerBackPhoto(e.target.value)} placeholder="https://..." className="bg-card border-border rounded-none" data-testid="input-ver-back-photo" />
              </div>
            </div>

            <Button onClick={handleCreateVersion} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="create-version-btn">
              {submitting ? 'Creating...' : 'Create Version'} <Check className="w-4 h-4 ml-1" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
