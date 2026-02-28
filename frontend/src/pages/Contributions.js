import api from '@/lib/api';
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getSubmissions, getReports, voteOnSubmission, voteOnReport, createSubmission, getMasterKits, createTeamPending, createBrandPending, createLeaguePending } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { ThumbsUp, ThumbsDown, Shirt, FileCheck, AlertTriangle, Plus, Check, Clock, X, ChevronDown, ChevronUp, ArrowRight, ArrowLeft, Image } from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const MODELS = ['Authentic', 'Replica', 'Other'];
const GENDERS = ['Man', 'Woman', 'Kid'];
const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];


const FIELD_LABELS = {
  club: 'Club / Team',
  season: 'Season',
  kit_type: 'Type',
  brand: 'Brand',
  design: 'Design',
  sponsor: 'Sponsor',
  league: 'League',
  gender: 'Gender',
  front_photo: 'Front Photo',
  back_photo: 'Back Photo',
  competition: 'Competition',
  model: 'Model',
  sku_code: 'SKU Code',
  ean_code: 'EAN Code',
  kit_id: 'Parent Kit',
  version_id: 'Version ID',
  created_by: 'Created By',
  created_at: 'Created At',
  name: 'Name',
  full_name: 'Full Name',
  country: 'Country',
  city: 'City',
  founded: 'Founded',
  primary_color: 'Primary Color',
  secondary_color: 'Secondary Color',
  crest_url: 'Crest / Badge',
  logo_url: 'Logo',
  photo_url: 'Photo',
  country_or_region: 'Country / Region',
  level: 'Level',
  organizer: 'Organizer',
  nationality: 'Nationality',
  birth_year: 'Birth Year',
  positions: 'Positions',
  preferred_number: 'Preferred Number',
};

const ENTITY_DISPLAY_FIELDS = {
  team: ['name', 'country', 'city', 'founded', 'primary_color', 'secondary_color'],
  league: ['name', 'country_or_region', 'level', 'organizer'],
  brand: ['name', 'country', 'founded'],
  player: ['full_name', 'nationality', 'birth_year', 'positions', 'preferred_number'],
};

const ENTITY_IMAGE_FIELDS = { team: 'crest_url', league: 'logo_url', brand: 'logo_url', player: 'photo_url' };

const TYPE_LABELS = {
  master_kit: 'Master Kit', version: 'Version',
  team: 'Team', league: 'League', brand: 'Brand', player: 'Player',
};

function SubmissionDetail({ sub, existingKits, searchExistingKit }) {
  const isEntity = ['team', 'league', 'brand', 'player'].includes(sub.submission_type);
  const fields = isEntity
    ? (ENTITY_DISPLAY_FIELDS[sub.submission_type] || [])
    : sub.submission_type === 'master_kit'
      ? ['club', 'season', 'kit_type', 'brand', 'league', 'design', 'sponsor', 'gender']
      : ['competition', 'model', 'sku_code', 'ean_code'];
  const parentKit = sub.submission_type === 'version' && existingKits.find(k => k.kit_id === sub.data?.kit_id);

const filteredExistingKits = existingKits.filter((k) => {
  const label = `${k.club} ${k.season} ${k.type}`.toLowerCase();
  const query = searchExistingKit.toLowerCase();
  return label.includes(query);
});


  return (
    <div className="mt-4 pt-4 border-t border-border" data-testid={`submission-detail-${sub.submission_id}`}>
      {isEntity && sub.data?.mode && (
        <div className="mb-3">
          <Badge variant="outline" className="rounded-none text-[10px]">
            {sub.data.mode === 'create' ? 'New Entity' : 'Edit Suggestion'}
          </Badge>
          {sub.data.mode === 'edit' && sub.data.entity_id && (
            <span className="text-[10px] font-mono text-muted-foreground ml-2">{sub.data.entity_id}</span>
          )}
        </div>
      )}
      {parentKit && (
        <div className="mb-3 p-3 bg-secondary/30 border border-border">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Parent Master Kit</p>
          <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            {parentKit.club} - {parentKit.season} ({parentKit.kit_type})
          </p>
        </div>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {fields.map(field => (
          <div key={field} className="space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
              {FIELD_LABELS[field] || field}
            </p>
            <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              {sub.data?.[field] || '—'}
            </p>
          </div>
        ))}
      </div>
      {sub.data?.front_photo && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>Photo</p>
          <img src={sub.data.front_photo} alt="Jersey" className="w-24 h-32 object-cover border border-border" />
        </div>
      )}
      {isEntity && ENTITY_IMAGE_FIELDS[sub.submission_type] && sub.data?.[ENTITY_IMAGE_FIELDS[sub.submission_type]] && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>
            {FIELD_LABELS[ENTITY_IMAGE_FIELDS[sub.submission_type]] || 'Image'}
          </p>
          <img src={sub.data[ENTITY_IMAGE_FIELDS[sub.submission_type]]} alt="" className="w-20 h-20 object-contain border border-border bg-secondary" />
        </div>
      )}
    </div>
  );
}

function ReportDetail({ rep }) {
  const skipFields = ['_id', 'kit_id', 'version_id', 'created_by', 'created_at', 'version_count', 'avg_rating', 'review_count'];
  const allFields = [...new Set([
    ...Object.keys(rep.original_data || {}).filter(f => !skipFields.includes(f)),
    ...Object.keys(rep.corrections || {}).filter(f => !skipFields.includes(f))
  ])];

  return (
    <div className="mt-4 pt-4 border-t border-border" data-testid={`report-detail-${rep.report_id}`}>
      <div className="grid grid-cols-[1fr,1fr,1fr] gap-0 text-[10px] uppercase tracking-wider text-muted-foreground mb-2 px-2" style={{ fontFamily: 'Barlow Condensed' }}>
        <span>Field</span>
        <span>Current</span>
        <span>Proposed</span>
      </div>
      {allFields.map(field => {
        const original = rep.original_data?.[field];
        const proposed = rep.corrections?.[field];
        const changed = proposed !== undefined && String(proposed) !== String(original);
        const isPhoto = field.includes('photo');
        return (
          <div key={field} className={`grid grid-cols-[1fr,1fr,1fr] gap-0 py-2 px-2 border-t border-border/30 ${changed ? 'bg-primary/5' : ''}`}>
            <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>
              {FIELD_LABELS[field] || field}
            </span>
            {isPhoto ? (
              <>
                <div>{original ? <img src={original} alt="" className="w-12 h-16 object-cover border border-border" /> : <span className="text-xs text-muted-foreground">—</span>}</div>
                <div>{changed && proposed ? <img src={proposed} alt="" className="w-12 h-16 object-cover border border-primary/30" /> : <span className="text-xs text-muted-foreground">—</span>}</div>
              </>
            ) : (
              <>
                <span className={`text-sm ${changed ? 'line-through text-muted-foreground/50' : ''}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  {original !== undefined && original !== null ? String(original) : '—'}
                </span>
                <span className={`text-sm ${changed ? 'text-primary font-medium' : 'text-muted-foreground'}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  {changed ? String(proposed) : '—'}
                </span>
              </>
            )}
          </div>
        );
      })}
      {rep.notes && (
        <div className="mt-3 p-3 bg-secondary/30 border border-border">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Reporter Notes</p>
          <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{rep.notes}</p>
        </div>
      )}
    </div>
  );
}

export default function Contributions() {
  // Recherche dans "Use Existing Kit"
  const [searchExistingKit, setSearchExistingKit] = useState("");
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('pending');
  const [submissions, setSubmissions] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addStep, setAddStep] = useState(1);
  const [subType, setSubType] = useState('master_kit');
  const [existingKits, setExistingKits] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [expandedSubmission, setExpandedSubmission] = useState(null);
  const [expandedReport, setExpandedReport] = useState(null);
  const [pendingEntities, setPendingEntities] = useState({
  team: [], league: [], brand: [], player: []
});
const [loadingPending, setLoadingPending] = useState(false);

  // Master Kit form fields
  const [club, setClub] = useState('');
  const [teamId, setTeamId] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [brandId, setBrandId] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [design, setDesign] = useState('');
  const [sponsor, setSponsor] = useState('');
  const [league, setLeague] = useState('');
  const [leagueId, setLeagueId] = useState('');
  const [gender, setGender] = useState('');

  // Version form fields
  const [selectedKit, setSelectedKit] = useState('');
  const [competition, setCompetition] = useState('');
  const [model, setModel] = useState('');
  const [skuCode, setSkuCode] = useState('');
  const [eanCode, setEanCode] = useState('');
  const [verFrontPhoto, setVerFrontPhoto] = useState('');
  const [verBackPhoto, setVerBackPhoto] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const status = activeTab === 'approved' ? 'approved' : 'pending';
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status }),
        getReports({ status })
      ]);
      setSubmissions(subsRes.data);
      setReports(repsRes.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  };

useEffect(() => {
  // Fetch des submissions et rapports
  const fetchData = async () => {
    setLoading(true);
    try {
      const status = activeTab === 'approved' ? 'approved' : 'pending';
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status }),
        getReports({ status })
      ]);
      setSubmissions(subsRes.data);
      setReports(repsRes.data);
    } catch (e) {
      console.error('Failed to fetch submissions', e);
    } finally {
      setLoading(false);
    }
  };

  // Fetch des entités en attente
  const fetchPendingEntities = async () => {
    setLoadingPending(true);
    try {
      const res = await api.get('/pending');
      setPendingEntities({
        team: res.data.team || [],
        league: res.data.league || [],
        brand: res.data.brand || [],
        player: res.data.player || [],
      });
    } catch (e) {
      console.error('Failed to fetch pending entities', e);
      setPendingEntities({ team: [], league: [], brand: [], player: [] });
    } finally {
      setLoadingPending(false);
    }
  };

  // Fetch des kits existants
  const fetchExistingKits = async () => {
    try {
      const res = await api.get('/master-kits');
      setExistingKits(res.data || []);
    } catch (e) {
      console.error('Failed to fetch existing kits', e);
      setExistingKits([]);
    }
  };

  // Exécuter tous les fetch
  fetchData();
  fetchPendingEntities();
  fetchExistingKits();
}, [activeTab]);



  const handleVoteSub = async (subId, vote) => {
    try {
      await voteOnSubmission(subId, vote);
      toast.success(`Vote recorded: ${vote}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handleVoteReport = async (repId, vote) => {
    try {
      await voteOnReport(repId, vote);
      toast.success(`Vote recorded: ${vote}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handleSubmitKit = async () => {
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

if (brand && !brandId) {
  try {
    const res = await createBrandPending({ name: brand });
    resolvedBrandId = res.data?.brand_id;
    toast.info(`Marque "${brand}" créée — en attente de validation`);
  } catch (e) { console.warn('createBrandPending failed:', e); }
}

if (league && !leagueId) {
  try {
    const res = await createLeaguePending({ name: league });
    resolvedLeagueId = res.data?.league_id;
    toast.info(`Ligue "${league}" créée — en attente de validation`);
  } catch (e) { console.warn('createLeaguePending failed:', e); }
}

    setSubmitting(true);
    try {
const data = { 
  club, 
  season, 
  kit_type: kitType, 
  brand, 
  front_photo: frontPhoto, 
  design, 
  sponsor,
  league,
  gender,
  team_id: resolvedTeamId || undefined,
  brand_id: resolvedBrandId || undefined,
  league_id: resolvedLeagueId || undefined
};
      await createSubmission({ submission_type: 'master_kit', data });
      toast.success('Master Kit submitted for community review!');
      setAddStep(2);
      setSubType('version');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitVersion = async () => {
    if (!selectedKit || !competition || !model) {
      toast.error('Please fill all required fields (Parent Kit, Competition, Model)');
      return;
    }
    setSubmitting(true);
    try {
      const data = { kit_id: selectedKit, competition, model, sku_code: skuCode, ean_code: eanCode, front_photo: verFrontPhoto, back_photo: verBackPhoto };
      await createSubmission({ submission_type: 'version', data });
      toast.success('Version submitted for community review!');
      closeAddForm();
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const closeAddForm = () => {
    setShowAddForm(false);
    setAddStep(1);
    setSubType('master_kit');
    setClub(''); setTeamId(''); setSeason(''); setKitType(''); setBrand(''); setBrandId('');
    setFrontPhoto(''); setDesign(''); setSponsor(''); setLeague(''); setLeagueId(''); setGender('');
    setSelectedKit(''); setCompetition(''); setModel('');
    setSkuCode(''); setEanCode(''); setVerFrontPhoto(''); setVerBackPhoto('');
  };

  const hasVoted = (item) => item.voters?.includes(user?.user_id);
  const isModerator = user?.role === 'moderator' || user?.role === 'admin';

  const filteredExistingKits = existingKits.filter((k) => {
  const label = `${k.club} ${k.season} ${k.type}`.toLowerCase();
  const query = searchExistingKit.toLowerCase();
  return label.includes(query);
});

  

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="contributions-title">
                CONTRIBUTIONS
              </h1>
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                Submit new jerseys and vote on community contributions. {isModerator ? 'As a moderator, your upvote approves instantly.' : '5 upvotes required for approval.'}
              </p>
              {isModerator && (
                <Badge className="mt-2 rounded-none bg-primary/20 text-primary border-primary/30" data-testid="moderator-badge">
                  Moderator
                </Badge>
              )}
            </div>
            <Button
              onClick={() => setShowAddForm(!showAddForm)}
              className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0"
              data-testid="add-jersey-btn"
            >
              <Plus className="w-4 h-4 mr-1" /> Add Jersey
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8">
        {/* Add Jersey Form */}
        {showAddForm && (
          <div className="border border-primary/30 p-6 mb-8" data-testid="add-jersey-form">
            {/* Step indicator */}
            <div className="flex items-center gap-4 mb-6">
              <div className={`flex items-center gap-2 ${addStep === 1 ? 'text-primary' : 'text-muted-foreground'}`}>
                <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 1 ? 'bg-primary text-primary-foreground' : addStep > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                  {addStep > 1 ? <Check className="w-3 h-3" /> : '1'}
                </div>
                <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>MASTER KIT</span>
              </div>
              <div className="w-8 h-px bg-border" />
              <div className={`flex items-center gap-2 ${addStep === 2 ? 'text-primary' : 'text-muted-foreground'}`}>
                <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 2 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'}`}>
                  2
                </div>
                <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>VERSION</span>
              </div>
            </div>

            {addStep === 1 && (
  <div>
    {/* Use existing kit option */}
    <div className="border border-border p-4 mb-4">
      <h4
        className="text-xs uppercase tracking-wider mb-3"
        style={{ fontFamily: "Barlow Condensed" }}
      >
        Use Existing Kit
      </h4>

      {/* Champ de recherche */}
      <input
        type="text"
        placeholder="Search kits (team, season, type)"
        value={searchExistingKit}
        onChange={(e) => setSearchExistingKit(e.target.value)}
        className="w-full mb-2 bg-card border border-border px-3 py-2 text-xs"
        style={{ fontFamily: "Barlow Condensed" }}
      />

      {/* Select filtré */}
      <Select
        value={selectedKit}
        onValueChange={(value) => setSelectedKit(value)}
        data-testid="select-existing-kit"
      >
        <SelectTrigger className="bg-card border-border rounded-none">
          <SelectValue placeholder="Select an existing Master Kit" />
        </SelectTrigger>
        <SelectContent className="bg-card border-border max-h-60">
          {filteredExistingKits.map((k) => (
            <SelectItem key={k._id} value={k.kit_id}>
              {k.club} – {k.season} ({k.type})
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {selectedKit && (
        <Button
          onClick={() => {
            setAddStep(2);
            setSubType("version");
          }}
          className="mt-3 rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
          data-testid="use-existing-kit-btn"
        >
          Continue with this Kit <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      )}
    </div>

    <div
      className="text-center text-xs text-muted-foreground tracking-wider my-4"
      style={{ fontFamily: "Barlow Condensed" }}
    >
      OR CREATE NEW
    </div>

    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Team *
        </Label>
        <EntityAutocomplete
  entityType="team"
  value={club}
  onChange={(val) => { setClub(val); setTeamId(''); }}
  onSelect={(item) => { setClub(item.label); setTeamId(item.id); }}
  placeholder="e.g., FC Barcelona"
  className="bg-card border-border rounded-none"
  testId="add-club"
/>


      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Season *
        </Label>
        <Input
          value={season}
          onChange={(e) => setSeason(e.target.value)}
          placeholder="e.g., 2024/2025"
          className="bg-card border-border rounded-none"
          data-testid="add-season"
        />
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          League
        </Label>
        <EntityAutocomplete
  entityType="league"
  value={league}
  onChange={(val) => { setLeague(val); setLeagueId(''); }}
  onSelect={(item) => { setLeague(item.label); setLeagueId(item.id); }}
  placeholder="e.g., Ligue 1"
  className="bg-card border-border rounded-none"
  testId="add-league"
/>
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Type *
        </Label>
        <Select value={kitType} onValueChange={setKitType}>
          <SelectTrigger
            className="bg-card border-border rounded-none"
            data-testid="add-kit-type"
          >
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {KIT_TYPES.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Brand *
        </Label>
        <EntityAutocomplete
  entityType="brand"
  value={brand}
  onChange={(val) => { setBrand(val); setBrandId(''); }}
  onSelect={(item) => { setBrand(item.label); setBrandId(item.id); }}
  placeholder="e.g., Nike"
  className="bg-card border-border rounded-none"
  testId="add-brand"
/>
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Design
        </Label>
        <Input
          value={design}
          onChange={(e) => setDesign(e.target.value)}
          placeholder="e.g., Single stripe"
          className="bg-card border-border rounded-none"
          data-testid="add-design"
        />
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Sponsor
        </Label>
        <Input
          value={sponsor}
          onChange={(e) => setSponsor(e.target.value)}
          placeholder="e.g., Qatar Airways"
          className="bg-card border-border rounded-none"
          data-testid="add-sponsor"
        />
      </div>

      <div className="space-y-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Gender
        </Label>
        <Select value={gender} onValueChange={setGender}>
          <SelectTrigger
            className="bg-card border-border rounded-none"
            data-testid="add-gender"
          >
            <SelectValue placeholder="Select gender" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {GENDERS.map((g) => (
              <SelectItem key={g} value={g}>
                {g}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2 sm:col-span-2">
        <Label
          className="text-xs uppercase tracking-wider"
          style={{ fontFamily: "Barlow Condensed" }}
        >
          Front Photo *
        </Label>
        <ImageUpload
          value={frontPhoto}
          onChange={setFrontPhoto}
          testId="add-front-photo"
        />
      </div>
    </div>

    <div className="flex gap-2 mt-6">
      <Button
        onClick={handleSubmitKit}
        disabled={submitting}
        className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
        data-testid="submit-kit-btn"
      >
        {submitting ? "Submitting..." : "Submit Master Kit"}{" "}
        <ArrowRight className="w-4 h-4 ml-1" />
      </Button>
      <Button
        variant="outline"
        onClick={closeAddForm}
        className="rounded-none"
        data-testid="cancel-add-btn"
      >
        Cancel
      </Button>
    </div>
  </div>
)}


            {addStep === 2 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <button onClick={() => setAddStep(1)} className="text-muted-foreground hover:text-foreground" data-testid="back-to-step-1">
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                    ADDING VERSION {selectedKit ? `TO ${existingKits.find(k => k.kit_id === selectedKit)?.club || 'SELECTED KIT'}` : 'TO NEW KIT (PENDING)'}
                  </span>
                </div>

                {!selectedKit && (
                  <div className="mb-4">
                    <Label className="text-xs uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed' }}>Select Parent Kit *</Label>
                    <Select value={selectedKit} onValueChange={setSelectedKit}>
                      <SelectTrigger className="bg-card border-border rounded-none" data-testid="version-kit-select">
                        <SelectValue placeholder="Select a Master Kit" />
                      </SelectTrigger>
                      <SelectContent className="bg-card border-border max-h-60">
                        {existingKits.map(k => (
                          <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Competition *</Label>
                    <Select value={competition} onValueChange={setCompetition}>
                      <SelectTrigger className="bg-card border-border rounded-none" data-testid="add-competition"><SelectValue placeholder="Select competition" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        {COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Model *</Label>
                    <Select value={model} onValueChange={setModel}>
                      <SelectTrigger className="bg-card border-border rounded-none" data-testid="add-model"><SelectValue placeholder="Select model" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                    <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" data-testid="add-sku" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EAN Code</Label>
                    <Input value={eanCode} onChange={e => setEanCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" data-testid="add-ean" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                    <ImageUpload value={verFrontPhoto} onChange={setVerFrontPhoto} testId="add-ver-front-photo" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Back Photo</Label>
                    <ImageUpload value={verBackPhoto} onChange={setVerBackPhoto} testId="add-ver-back-photo" />
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <Button onClick={handleSubmitVersion} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="submit-version-btn">
                    {submitting ? 'Submitting...' : 'Submit Version for Review'} <Check className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none" data-testid="cancel-version-btn">
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-card border border-border rounded-none mb-6">
            <TabsTrigger value="pending" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground" data-testid="tab-pending">
              <Clock className="w-3 h-3 mr-1" /> Pending
            </TabsTrigger>
            <TabsTrigger value="approved" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground" data-testid="tab-approved">
              <Check className="w-3 h-3 mr-1" /> Approved
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {/* Submissions */}
            <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
              <Shirt className="w-4 h-4 inline mr-1" /> JERSEY SUBMISSIONS
            </h3>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => <div key={i} className="h-20 bg-card animate-pulse border border-border" />)}
              </div>
            ) : submissions.length === 0 ? (
              <div className="text-center py-10 border border-dashed border-border mb-8">
                <FileCheck className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                  No {activeTab} submissions
                </p>
              </div>
            ) : (
              <div className="space-y-3 mb-8" data-testid="submissions-list">
                {submissions.map(sub => (
                  <div key={sub.submission_id} className="border border-border bg-card" data-testid={`submission-${sub.submission_id}`}>
                    <div
                      className="flex items-start justify-between gap-4 p-4 cursor-pointer hover:bg-secondary/20"
                      style={{ transition: 'background-color 0.2s' }}
                      onClick={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                      data-testid={`submission-toggle-${sub.submission_id}`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                          {['team', 'league', 'brand', 'player'].includes(sub.submission_type) && (
                            <Badge variant="outline" className="rounded-none text-[10px] border-primary/30 text-primary">
                              {sub.data?.mode === 'edit' ? 'Edit' : 'New'}
                            </Badge>
                          )}
                          <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>
                            {sub.status}
                          </Badge>
                        </div>
                        <h4 className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {sub.submission_type === 'master_kit'
                            ? `${sub.data?.club || '?'} - ${sub.data?.season || '?'} (${sub.data?.kit_type || '?'})`
                            : sub.submission_type === 'version'
                            ? `${sub.data?.competition || '?'} - ${sub.data?.model || '?'}`
                            : sub.submission_type === 'player'
                            ? (sub.data?.full_name || '?')
                            : (sub.data?.name || '?')}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          by {sub.submitter_name || 'Unknown'} -- {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-center">
                          <div className="flex items-center gap-1">
                            <span className="font-mono text-sm text-primary">{sub.votes_up}</span>
                            <span className="text-muted-foreground">/</span>
                            <span className="font-mono text-sm text-destructive">{sub.votes_down}</span>
                          </div>
                          <span className="text-[10px] text-muted-foreground">votes</span>
                        </div>
                        {sub.status === 'pending' && !hasVoted(sub) && (
                          <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                            <button onClick={() => handleVoteSub(sub.submission_id, 'up')} className="p-2 border border-border hover:border-primary hover:text-primary" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-up-${sub.submission_id}`}>
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleVoteSub(sub.submission_id, 'down')} className="p-2 border border-border hover:border-destructive hover:text-destructive" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-down-${sub.submission_id}`}>
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                        {hasVoted(sub) && (
                          <Badge variant="secondary" className="rounded-none text-[10px]">Voted</Badge>
                        )}
                        {expandedSubmission === sub.submission_id
                          ? <ChevronUp className="w-4 h-4 text-muted-foreground" />
                          : <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        }
                      </div>
                    </div>
                    {expandedSubmission === sub.submission_id && (
                      <div className="px-4 pb-4">
                        <SubmissionDetail 
                         sub={sub} 
                         existingKits={existingKits} 
                        searchExistingKit={searchExistingKit} 
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
{/* Références à valider */}
{activeTab === 'pending' && (
  <div className="mb-10">
    <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
      <AlertTriangle className="w-4 h-4 inline mr-1" /> RÉFÉRENCES À VALIDER
    </h3>
    {loadingPending ? (
      <div className="h-16 bg-card animate-pulse border border-border" />
    ) : Object.values(pendingEntities).every(arr => arr.length === 0) ? (
      <div className="text-center py-8 border border-dashed border-border mb-8">
        <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
          Aucune référence en attente de validation
        </p>
      </div>
    ) : (
      <div className="space-y-4 mb-8">
        {[
          { key: 'team', label: 'Équipes' },
          { key: 'league', label: 'Compétitions' },
          { key: 'brand', label: 'Marques' },
          { key: 'player', label: 'Joueurs' },
        ].map(({ key, label }) => {
          const list = pendingEntities[key] || [];
          if (!list.length) return null;
          return (
            <div key={key} className="border border-border bg-card p-4">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>
                {label} ({list.length})
              </p>
              <div className="space-y-2">
                {list.map(item => (
                  <div key={item.team_id || item.league_id || item.brand_id || item.player_id || item._id}
                    className="flex items-center justify-between px-3 py-2 bg-secondary/30 border border-border/50">
                    <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                      {item.name || item.full_name || '—'}
                    </span>
                    <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent">
                      for review
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    )}
  </div>
)}

            {/* Reports */}
            <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
              <AlertTriangle className="w-4 h-4 inline mr-1" /> CORRECTION REPORTS
            </h3>
            {reports.length === 0 ? (
              <div className="text-center py-10 border border-dashed border-border">
                <AlertTriangle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                  No {activeTab} reports
                </p>
              </div>
            ) : (
              <div className="space-y-3" data-testid="reports-list">
                {reports.map(rep => (
                  <div key={rep.report_id} className="border border-border bg-card" data-testid={`report-${rep.report_id}`}>
                    <div
                      className="flex items-start justify-between gap-4 p-4 cursor-pointer hover:bg-secondary/20"
                      style={{ transition: 'background-color 0.2s' }}
                      onClick={() => setExpandedReport(expandedReport === rep.report_id ? null : rep.report_id)}
                      data-testid={`report-toggle-${rep.report_id}`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <Badge variant="outline" className="rounded-none text-[10px]">{rep.target_type === 'master_kit' ? 'Kit Correction' : 'Version Correction'}</Badge>
                          <Badge className={`rounded-none text-[10px] ${rep.status === 'approved' ? 'bg-primary/20 text-primary' : 'bg-accent/20 text-accent'}`}>
                            {rep.status}
                          </Badge>
                        </div>
                        <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {rep.notes || 'Correction submitted'}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          by {rep.reporter_name || 'Unknown'} -- {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-center">
                          <div className="flex items-center gap-1">
                            <span className="font-mono text-sm text-primary">{rep.votes_up}</span>
                            <span className="text-muted-foreground">/</span>
                            <span className="font-mono text-sm text-destructive">{rep.votes_down}</span>
                          </div>
                          <span className="text-[10px] text-muted-foreground">votes</span>
                        </div>
                        {rep.status === 'pending' && !hasVoted(rep) && (
                          <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                            <button onClick={() => handleVoteReport(rep.report_id, 'up')} className="p-2 border border-border hover:border-primary hover:text-primary" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-up-rep-${rep.report_id}`}>
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleVoteReport(rep.report_id, 'down')} className="p-2 border border-border hover:border-destructive hover:text-destructive" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-down-rep-${rep.report_id}`}>
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                        {hasVoted(rep) && (
                          <Badge variant="secondary" className="rounded-none text-[10px]">Voted</Badge>
                        )}
                        {expandedReport === rep.report_id
                          ? <ChevronUp className="w-4 h-4 text-muted-foreground" />
                          : <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        }
                      </div>
                    </div>
                    {expandedReport === rep.report_id && (
                      <div className="px-4 pb-4">
                        <ReportDetail rep={rep} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
