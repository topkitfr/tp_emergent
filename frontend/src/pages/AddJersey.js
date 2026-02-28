import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {  createMasterKit, createVersion, getMasterKits, createTeamPending, createLeaguePending, createBrandPending } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowRight, ArrowLeft, Check } from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import AutocompleteInput from '@/components/AutocompleteInput';
import EntityAutocomplete from '@/components/EntityAutocomplete';

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

  const [club, setClub] = useState('');
  const [teamId, setTeamId] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [brandId, setBrandId] = useState('');
  const [design, setDesign] = useState('');
  const [sponsor, setSponsor] = useState('');
  const [gender, setGender] = useState('');
  const [league, setLeague] = useState('');
  const [leagueId, setLeagueId] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');

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
      let resolvedTeamId = teamId;
      let resolvedBrandId = brandId;
      let resolvedLeagueId = leagueId;

      if (club && !teamId) {
  try {
    const res = await createTeamPending({ name: club });
    resolvedTeamId = res.data?.team_id;
    toast.info(`Équipe "${club}" créée — en attente de validation`);
  } catch (e) { console.warn('createTeamPending failed:', e); }
}

      const res = await createMasterKit({
        club,
        season,
        kit_type: kitType,
        brand,
        front_photo: frontPhoto,
        design,
        sponsor,
        gender,
        league,
        team_id: resolvedTeamId || undefined,
        brand_id: resolvedBrandId || undefined,
        league_id: resolvedLeagueId || undefined,
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
    if (!kitId) {
      toast.error('Please select or create a Master Kit first');
      return;
    }
    if (!competition || !model) {
      toast.error('Please fill Competition and Model');
      return;
    }
    setSubmitting(true);
    try {
      const res = await createVersion({
        kit_id: kitId,
        competition,
        model,
        sku_code: skuCode,
        ean_code: eanCode,
        front_photo: verFrontPhoto,
        back_photo: verBackPhoto,
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
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-black uppercase mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>
          ADD JERSEY
        </h1>
        <p className="text-sm text-muted-foreground mb-8" style={{ fontFamily: 'DM Sans' }}>
          Contribute to the catalog by adding new kits and versions
        </p>

        {/* Step indicator */}
        <div className="flex items-center gap-3 mb-8">
          <div className={`w-8 h-8 flex items-center justify-center text-sm font-bold ${step > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
            {step > 1 ? <Check className="w-4 h-4" /> : '1'}
          </div>
          <span className={`text-xs uppercase tracking-wider ${step === 1 ? 'text-foreground' : 'text-muted-foreground'}`} style={fieldStyle}>
            MASTER KIT
          </span>
          <ArrowRight className="w-4 h-4 text-muted-foreground" />
          <div className={`w-8 h-8 flex items-center justify-center text-sm font-bold ${step === 2 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
            2
          </div>
          <span className={`text-xs uppercase tracking-wider ${step === 2 ? 'text-foreground' : 'text-muted-foreground'}`} style={fieldStyle}>
            VERSION
          </span>
        </div>

        {step === 1 && (
          <div className="space-y-6">
            {/* Use existing kit */}
            <div className="border border-border p-4 bg-card">
              <h3 className="text-xs uppercase tracking-wider font-bold mb-4" style={fieldStyle}>
                USE EXISTING KIT
              </h3>
              <Select value={selectedExistingKit} onValueChange={(v) => setSelectedExistingKit(v)}>
                <SelectTrigger className={inputClass} data-testid="select-existing-kit">
                  <SelectValue placeholder="Select an existing Master Kit" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border max-h-60">
                  {existingKits.map(k => (
                    <SelectItem key={k.kit_id} value={k.kit_id}>
                      {k.club} - {k.season} ({k.kit_type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedExistingKit && (
                <Button
                  onClick={() => setStep(2)}
                  className="mt-3 rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
                  data-testid="use-existing-kit-btn"
                >
                  Continue with this Kit <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>

            <div className="flex items-center gap-4">
              <div className="flex-1 border-t border-border" />
              <span className="text-xs uppercase tracking-wider text-muted-foreground" style={fieldStyle}>OR CREATE NEW</span>
              <div className="flex-1 border-t border-border" />
            </div>

            {/* Create new kit form */}
            <div className="space-y-4">
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Team *</Label>
               <EntityAutocomplete
  entityType="team"
  value={club}
  onChange={(val) => { setClub(val); setTeamId(''); }}
  onSelect={(item) => { setClub(item.label); setTeamId(item.id); }}
  placeholder="e.g., FC Barcelona"
  className={inputClass}
  testId="input-club"
/>

              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Season *</Label>
                <Input value={season} onChange={e => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className={inputClass} data-testid="input-season" />
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Type *</Label>
                <Select value={kitType} onValueChange={setKitType}>
                  <SelectTrigger className={inputClass} data-testid="select-kit-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Brand *</Label>
                <EntityAutocomplete
  entityType="brand"
  value={brand}
  onChange={(val) => { setBrand(val); setBrandId(''); }}
  onSelect={(item) => { setBrand(item.label); setBrandId(item.id); }}
  placeholder="e.g., Nike"
  className={inputClass}
  testId="input-brand"
/>
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Design</Label>
                <Input value={design} onChange={e => setDesign(e.target.value)} placeholder="e.g., Single stripe" className={inputClass} data-testid="input-design" />
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Sponsor</Label>
                <Input value={sponsor} onChange={e => setSponsor(e.target.value)} placeholder="e.g., Qatar Airways" className={inputClass} data-testid="input-sponsor" />
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Gender</Label>
                <Select value={gender} onValueChange={setGender}>
                  <SelectTrigger className={inputClass} data-testid="select-gender">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>League</Label>
                <EntityAutocomplete
  entityType="league"
  value={league}
  onChange={(val) => { setLeague(val); setLeagueId(''); }}
  onSelect={(item) => { setLeague(item.label); setLeagueId(item.id); }}
  placeholder="e.g., Ligue 1"
  className={inputClass}
  testId="input-league"
/>
              </div>
              <div>
                <Label className={fieldLabel} style={fieldStyle}>Front Photo *</Label>
                <ImageUpload onUpload={setFrontPhoto} testId="upload-front-photo" />
              </div>
              <Button
                onClick={handleCreateKit}
                disabled={submitting}
                className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
                data-testid="create-kit-btn"
              >
                {submitting ? 'Creating...' : 'Create Master Kit'} <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-2">
              <button onClick={() => setStep(1)} className="text-muted-foreground hover:text-foreground" data-testid="back-to-step-1">
                <ArrowLeft className="w-4 h-4" />
              </button>
              <span className="text-xs uppercase tracking-wider" style={fieldStyle}>
                ADDING VERSION {createdKitId ? 'TO NEW KIT' : `TO ${existingKits.find(k => k.kit_id === selectedExistingKit)?.club || 'SELECTED KIT'}`}
              </span>
            </div>

            <div>
              <Label className={fieldLabel} style={fieldStyle}>Competition *</Label>
              <Select value={competition} onValueChange={setCompetition}>
                <SelectTrigger className={inputClass} data-testid="select-competition">
                  <SelectValue placeholder="Select competition" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className={fieldLabel} style={fieldStyle}>Model *</Label>
              <Select value={model} onValueChange={setModel}>
                <SelectTrigger className={inputClass} data-testid="select-model">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className={fieldLabel} style={fieldStyle}>SKU Code</Label>
              <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className={`${inputClass} font-mono`} data-testid="input-sku" />
            </div>
            <div>
              <Label className={fieldLabel} style={fieldStyle}>EAN Code</Label>
              <Input value={eanCode} onChange={e => setEanCode(e.target.value)} placeholder="Optional" className={`${inputClass} font-mono`} data-testid="input-ean" />
            </div>
            <div>
              <Label className={fieldLabel} style={fieldStyle}>Front Photo</Label>
              <ImageUpload onUpload={setVerFrontPhoto} testId="upload-ver-front-photo" />
            </div>
            <div>
              <Label className={fieldLabel} style={fieldStyle}>Back Photo</Label>
              <ImageUpload onUpload={setVerBackPhoto} testId="upload-ver-back-photo" />
            </div>
            <Button
              onClick={handleCreateVersion}
              disabled={submitting}
              className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="create-version-btn"
            >
              {submitting ? 'Creating...' : 'Create Version'} <Check className="w-4 h-4 ml-2" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
