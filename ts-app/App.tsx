import React, { useState } from 'react';
import { Equipment, CHECK_ITEMS, OPTIONS, DISPOSAL_OPTIONS } from './types';
import { generateInspectionPDF } from './pdfUtils';
import './style.css';

const defaultEquipment: Equipment = {
  firma: 'Nordic Maskin & Rail P/S',
  adresse: 'Krumtappen 5, 6580 Vamdrup',
  maskin_nr: '',
  fabrikat: '',
  model: '',
  serie_nr: '',
  aargang: '',
  timetaeller: '',
};


function App() {
  const [phase, setPhase] = useState(0);
  const [equipment, setEquipment] = useState<Equipment>(defaultEquipment);
  const [technician, setTechnician] = useState('');
  const [answers, setAnswers] = useState<string[]>(Array(CHECK_ITEMS.length).fill('OK'));
  const [comments, setComments] = useState<string[]>(Array(CHECK_ITEMS.length).fill(''));
  const [otherComment, setOtherComment] = useState('');
  const [discard, setDiscard] = useState('Nej');
  const [discardReason, setDiscardReason] = useState('');
  const [disposalAction, setDisposalAction] = useState(DISPOSAL_OPTIONS[0]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  const handleSave = async () => {
    if (answers.includes('Fejl') && comments.some((c, i) => answers[i] === 'Fejl' && !c.trim())) {
      alert('Comentariu obligatoriu pentru toate punctele marcate ca Fejl.');
      return;
    }
    if (discard === 'Ja' && !discardReason.trim()) {
      alert('Motivul pentru kassering este obligatoriu.');
      return;
    }
    if (discard === 'Ja' && !disposalAction.trim()) {
      alert('Alege o acțiune de mediu.');
      return;
    }
    const pdfBytes = await generateInspectionPDF(
      equipment,
      answers,
      comments,
      otherComment,
      discard,
      discardReason,
      disposalAction
    );
    const blobData = new Uint8Array(pdfBytes);
    const blob = new Blob([blobData], { type: 'application/pdf' });
    setPdfUrl(URL.createObjectURL(blob));
  };

  if (phase === 0) {
    return (
      <div className="app-container">
        <h1>🔧 Små-materiel eftersyn</h1>
        <h2 style={{ color: '#145da0', fontWeight: 500, marginBottom: 24 }}>Bekræft udstyr og mekaniker</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <input placeholder="Maskin nr." value={equipment.maskin_nr} onChange={e => setEquipment({ ...equipment, maskin_nr: e.target.value })} />
          <input placeholder="Fabrikat" value={equipment.fabrikat} onChange={e => setEquipment({ ...equipment, fabrikat: e.target.value })} />
          <input placeholder="Model" value={equipment.model} onChange={e => setEquipment({ ...equipment, model: e.target.value })} />
          <input placeholder="Serie nr." value={equipment.serie_nr} onChange={e => setEquipment({ ...equipment, serie_nr: e.target.value })} />
          <input placeholder="Årgang" value={equipment.aargang} onChange={e => setEquipment({ ...equipment, aargang: e.target.value })} />
          <input placeholder="Timetæller" value={equipment.timetaeller} onChange={e => setEquipment({ ...equipment, timetaeller: e.target.value })} />
        </div>
        <input placeholder="Mekaniker - dit navn" value={technician} onChange={e => setTechnician(e.target.value)} style={{ marginTop: 12 }} />
        <button style={{ width: '100%', marginTop: 18 }} onClick={() => setPhase(1)}>▶️ Start eftersyn</button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <h1>🔧 Små-materiel eftersyn</h1>
      <div style={{ color: '#555', marginBottom: 18, fontWeight: 500 }}>
        <span>Alle punkte pornesc ca OK. Selectează "Fejl" sau "ikke relevant" dacă este cazul.</span>
      </div>
      {CHECK_ITEMS.map((item, idx) => (
        <div key={idx} className="checklist-item">
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
            <strong style={{ flex: 1 }}>{item}</strong>
            <div className="radio-group">
              {OPTIONS.map(opt => (
                <label key={opt}>
                  <input
                    type="radio"
                    name={`status_${idx}`}
                    checked={answers[idx] === opt}
                    onChange={() => {
                      const newAnswers = [...answers];
                      newAnswers[idx] = opt;
                      setAnswers(newAnswers);
                    }}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>
          <textarea
            placeholder="Bemærkning..."
            value={comments[idx]}
            onChange={e => {
              const newComments = [...comments];
              newComments[idx] = e.target.value;
              setComments(newComments);
            }}
          />
        </div>
      ))}
      <textarea
        placeholder="Andre bemærkninger"
        value={otherComment}
        onChange={e => setOtherComment(e.target.value)}
        style={{ marginBottom: 18 }}
      />
      <div className="radio-group" style={{ marginBottom: 10 }}>
        <label>
          <input type="radio" checked={discard === 'Nej'} onChange={() => setDiscard('Nej')} /> Nu
        </label>
        <label>
          <input type="radio" checked={discard === 'Ja'} onChange={() => setDiscard('Ja')} /> Ja
        </label>
      </div>
      {discard === 'Ja' && (
        <div style={{ marginBottom: 10 }}>
          <select value={disposalAction} onChange={e => setDisposalAction(e.target.value)}>
            {DISPOSAL_OPTIONS.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          <textarea
            placeholder="Årsag til kassering"
            value={discardReason}
            onChange={e => setDiscardReason(e.target.value)}
            style={{ marginTop: 8 }}
          />
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 18 }}>
        <button onClick={() => setPhase(0)}>⬅️ Înapoi</button>
        <button onClick={handleSave}>💾 Generează PDF</button>
      </div>
      {pdfUrl && (
        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <a href={pdfUrl} download="eftersyn.pdf" style={{ fontWeight: 600, color: '#145da0', fontSize: '1.1em' }}>⬇️ Descarcă PDF</a>
        </div>
      )}
    </div>
  );
}

export default App;
