import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getSubmissions, getReports, voteOnSubmission, voteOnReport, createSubmission, getMasterKits } from '@/lib/api';
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

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special'];
const MODELS = ['Replica', 'Authentic', 'Player Issue'];
const GENDERS = ['Men', 'Women', 'Kids'];

const FIELD_LABELS = {
  club: 'Club / Team',
  season: 'Season',
  kit_type: 'Type',
  brand: 'Brand',
  year: 'Year',
  front_photo: 'Front Photo',
  back_photo: 'Back Photo',
  competition: 'Competition',
  model: 'Model',
  gender: 'Gender',
  sku_code: 'SKU Code',
  kit_id: 'Parent Kit',
  version_id: 'Version ID',
  created_by: 'Created By',
  created_at: 'Created At',
};

function SubmissionDetail({ sub, existingKits }) {
  const fields = sub.submission_type === 'master_kit'
    ? ['club', 'season', 'kit_type', 'brand', 'year']
    : ['competition', 'model', 'gender', 'sku_code'];
  const parentKit = sub.submission_type === 'version' && existingKits.find(k => k.kit_id === sub.data?.kit_id);

  return (
    <div className="mt-4 pt-4 border-t border-border" data-testid={`submission-detail-${sub.submission_id}`}>
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

  // Master Kit form fields
  const [club, setClub] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());

  // Version form fields
  const [selectedKit, setSelectedKit] = useState('');
  const [competition, setCompetition] = useState('');
  const [model, setModel] = useState('');
  const [gender, setGender] = useState('');
  const [skuCode, setSkuCode] = useState('');
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
    fetchData();
    getMasterKits({}).then(r => setExistingKits(r.data)).catch(() => {});
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
    if (!club || !season || !kitType || !brand) {
      toast.error('Please fill all required fields');
      return;
    }
    setSubmitting(true);
    try {
      const data = { club, season, kit_type: kitType, brand, front_photo: frontPhoto, year: parseInt(year) };
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
    if (!selectedKit || !competition || !model || !gender) {
      toast.error('Please fill all required fields');
      return;
    }
    setSubmitting(true);
    try {
      const data = { kit_id: selectedKit, competition, model, gender, sku_code: skuCode, front_photo: verFrontPhoto, back_photo: verBackPhoto };
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
    setClub(''); setSeason(''); setKitType(''); setBrand('');
    setFrontPhoto(''); setYear(new Date().getFullYear());
    setSelectedKit(''); setCompetition(''); setModel(''); setGender('');
    setSkuCode(''); setVerFrontPhoto(''); setVerBackPhoto('');
  };

  const hasVoted = (item) => item.voters?.includes(user?.user_id);

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
                Submit new jerseys and vote on community contributions. 5 upvotes required for approval.
              </p>
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
                  <h4 className="text-xs uppercase tracking-wider mb-3" style={{ fontFamily: 'Barlow Condensed' }}>Use Existing Kit</h4>
                  <Select value={selectedKit} onValueChange={setSelectedKit}>
                    <SelectTrigger className="bg-card border-border rounded-none" data-testid="select-existing-kit">
                      <SelectValue placeholder="Select an existing Master Kit" />
                    </SelectTrigger>
                    <SelectContent className="bg-card border-border max-h-60">
                      {existingKits.map(k => (
                        <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedKit && (
                    <Button onClick={() => { setAddStep(2); setSubType('version'); }} className="mt-3 rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="use-existing-kit-btn">
                      Continue with this Kit <ArrowRight className="w-4 h-4 ml-1" />
                    </Button>
                  )}
                </div>

                <div className="text-center text-xs text-muted-foreground tracking-wider my-4" style={{ fontFamily: 'Barlow Condensed' }}>
                  OR CREATE NEW
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Club / Team *</Label>
                    <Input value={club} onChange={e => setClub(e.target.value)} placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" data-testid="add-club" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
                    <Input value={season} onChange={e => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" data-testid="add-season" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Type *</Label>
                    <Select value={kitType} onValueChange={setKitType}>
                      <SelectTrigger className="bg-card border-border rounded-none" data-testid="add-kit-type"><SelectValue placeholder="Select type" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Brand *</Label>
                    <Input value={brand} onChange={e => setBrand(e.target.value)} placeholder="e.g., Nike" className="bg-card border-border rounded-none" data-testid="add-brand" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Year</Label>
                    <Input type="number" value={year} onChange={e => setYear(e.target.value)} className="bg-card border-border rounded-none" data-testid="add-year" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                    <ImageUpload value={frontPhoto} onChange={setFrontPhoto} testId="add-front-photo" />
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <Button onClick={handleSubmitKit} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="submit-kit-btn">
                    {submitting ? 'Submitting...' : 'Submit Master Kit'} <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none" data-testid="cancel-add-btn">
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
                    <Input value={competition} onChange={e => setCompetition(e.target.value)} placeholder="e.g., Champions League 2024/2025" className="bg-card border-border rounded-none" data-testid="add-competition" />
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
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Gender *</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger className="bg-card border-border rounded-none" data-testid="add-gender"><SelectValue placeholder="Select gender" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        {GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                    <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" data-testid="add-sku" />
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
                          <Badge variant="outline" className="rounded-none text-[10px]">{sub.submission_type === 'master_kit' ? 'Master Kit' : 'Version'}</Badge>
                          <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>
                            {sub.status}
                          </Badge>
                        </div>
                        <h4 className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {sub.submission_type === 'master_kit'
                            ? `${sub.data?.club || '?'} - ${sub.data?.season || '?'} (${sub.data?.kit_type || '?'})`
                            : `${sub.data?.competition || '?'} - ${sub.data?.model || '?'}`}
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
                        <SubmissionDetail sub={sub} existingKits={existingKits} />
                      </div>
                    )}
                  </div>
                ))}
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
