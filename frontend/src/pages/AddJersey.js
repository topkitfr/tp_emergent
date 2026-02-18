import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createMasterKit, createVersion, getMasterKits } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowRight, ArrowLeft, Check } from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import AutocompleteInput from '@/components/AutocompleteInput';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const MODELS = ['Authentic', 'Replica', 'Other'];
const GENDERS = ['Man', 'Woman', 'Kid'];
const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];

const fieldLabel = "text-xs uppercase tracking-wider";
const fieldStyle = { fontFamily: 'Barlow Condensed, sans-serif' };
const inputClass = "bg-card border-border rounded-none";

export default function AddJersey() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [existingKits, setExistingKits] = useState([]);
  const [selectedExistingKit, setSelectedExistingKit] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Master Kit fields
  const [club, setClub] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [design, setDesign] = useState('');
  const [sponsor, setSponsor] = useState('');
  const [gender, setGender] = useState('');
  const [league, setLeague] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');

  // Version fields
  const [competition, setCompetition] = useState('');
  const [model, setModel] = useState('');
  const [skuCode, setSkuCode] = useState('');
  const [eanCode, setEanCode] = useState('');
  const [verFrontPhoto, setVerFrontPhoto] = useState('');
  const [verBackPhoto, setVerBackPhoto] = useState('');

  const [createdKitId, setCreatedKitId] = useState('');

  useEffect(() => {
    getMasterKits({}).then(r => setExistingKits(r.data)).catch(() => {});
  }, []);

  const handleCreateKit = async () => {
    if (!club || !season || !kitType || !brand || !frontPhoto) {
      toast.error('Please fill all required fields (Team, Season, Type, Brand, Photo)');
      return;
    }
    setSubmitting(true);
    try {
      const res = await createMasterKit({
        club, season, kit_type: kitType, brand, front_photo: frontPhoto,
        design, sponsor, gender, league
      });
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
    if (!competition || !model) { toast.error('Please fill Competition and Model'); return; }
    setSubmitting(true);
    try {
      const res = await createVersion({
        kit_id: kitId, competition, model,
        sku_code: skuCode, ean_code: eanCode,
        front_photo: verFrontPhoto, back_photo: verBackPhoto
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
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="add-jersey-title">ADD JERSEY</h1>
          <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Contribute to the catalog by adding new kits and versions</p>
          <div className="flex items-center gap-4 mt-6">
            <div className={`flex items-center gap-2 ${step === 1 ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${step === 1 ? 'bg-primary text-primary-foreground' : step > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                {step > 1 ? <Check className="w-3 h-3" /> : '1'}
              </div>
              <span className="text-xs tracking-wider" style={fieldStyle}>MASTER KIT</span>
            </div>
            <div className="w-8 h-px bg-border" />
            <div className={`flex items-center gap-2 ${step === 2 ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${step === 2 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'}`}>2</div>
              <span className="text-xs tracking-wider" style={fieldStyle}>VERSION</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 lg:px-8 py-8">
        {step === 1 && (
          <div className="space-y-6" data-testid="step-1-form">
            <div className="border border-border p-6 mb-6">
              <h3 className="text-sm mb-4" style={fieldStyle}>USE EXISTING KIT</h3>
              <Select value={selectedExistingKit} onValueChange={(v) => { setSelectedExistingKit(v); }}>
                <SelectTrigger className={inputClass} data-testid="select-existing-kit"><SelectValue placeholder="Select an existing Master Kit" /></SelectTrigger>
                <SelectContent className="bg-card border-border max-h-60">
                  {existingKits.map(k => <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>)}
                </SelectContent>
              </Select>
              {selectedExistingKit && (
                <Button onClick={() => setStep(2)} className="mt-3 rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="use-existing-kit-btn">
                  Continue with this Kit <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </div>

            <div className="text-center text-xs text-muted-foreground tracking-wider" style={fieldStyle}>OR CREATE NEW</div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Team *</Label>
                <AutocompleteInput field="club" value={club} onChange={setClub} placeholder="e.g., FC Barcelona" className={inputClass} testId="input-club" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Season *</Label>
                <Input value={season} onChange={e => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className={inputClass} data-testid="input-season" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Type *</Label>
                <Select value={kitType} onValueChange={setKitType}>
                  <SelectTrigger className={inputClass} data-testid="select-kit-type"><SelectValue placeholder="Select type" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Brand *</Label>
                <AutocompleteInput field="brand" value={brand} onChange={setBrand} placeholder="e.g., Nike" className={inputClass} testId="input-brand" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Design</Label>
                <Input value={design} onChange={e => setDesign(e.target.value)} placeholder="e.g., Single stripe" className={inputClass} data-testid="input-design" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Sponsor</Label>
                <AutocompleteInput field="sponsor" value={sponsor} onChange={setSponsor} placeholder="e.g., Qatar Airways" className={inputClass} testId="input-sponsor" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Gender</Label>
                <Select value={gender} onValueChange={setGender}>
                  <SelectTrigger className={inputClass} data-testid="select-gender"><SelectValue placeholder="Select gender" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>League</Label>
                <AutocompleteInput field="league" value={league} onChange={setLeague} placeholder="e.g., Ligue 1" className={inputClass} testId="input-league" />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label className={fieldLabel} style={fieldStyle}>Front Photo *</Label>
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
              <button onClick={() => setStep(1)} className="text-muted-foreground hover:text-foreground" data-testid="back-to-step-1"><ArrowLeft className="w-4 h-4" /></button>
              <span className="text-xs text-muted-foreground" style={fieldStyle}>
                ADDING VERSION {createdKitId ? 'TO NEW KIT' : `TO ${existingKits.find(k => k.kit_id === selectedExistingKit)?.club || 'SELECTED KIT'}`}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Competition *</Label>
                <Select value={competition} onValueChange={setCompetition}>
                  <SelectTrigger className={inputClass} data-testid="select-competition"><SelectValue placeholder="Select competition" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Model *</Label>
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger className={inputClass} data-testid="select-model"><SelectValue placeholder="Select model" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>SKU Code</Label>
                <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className={`${inputClass} font-mono`} data-testid="input-sku" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>EAN Code</Label>
                <Input value={eanCode} onChange={e => setEanCode(e.target.value)} placeholder="Optional" className={`${inputClass} font-mono`} data-testid="input-ean" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Front Photo</Label>
                <ImageUpload value={verFrontPhoto} onChange={setVerFrontPhoto} label="Front" testId="upload-ver-front-photo" />
              </div>
              <div className="space-y-2">
                <Label className={fieldLabel} style={fieldStyle}>Back Photo</Label>
                <ImageUpload value={verBackPhoto} onChange={setVerBackPhoto} label="Back" testId="upload-ver-back-photo" />
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
