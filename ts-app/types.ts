// Tipuri și constante extrase din scriptul Python

export type Equipment = {
  firma: string;
  adresse: string;
  maskin_nr: string;
  fabrikat: string;
  model: string;
  serie_nr: string;
  aargang: string;
  timetaeller: string;
};

export const CHECK_ITEMS = [
  "Mekaniske dele",
  "Sikkerhedsudstyr",
  "Betjeningsanordninger",
  "Hydraulik og pneumatik",
  "Kæder og remme",
  "Smøring og vedligehold",
  "Bremser (hvis relevant)",
  "Oliestand",
  "Unormale lyder og vibrationer",
  "Dokumenteret i Trace Tool",
  "Påsætning af label for måned og år er sket",
];

export const OPTIONS = ["OK", "ikke relevant", "Fejl"];

export const DISPOSAL_OPTIONS = [
  "Bortskaffet",
  "Genanvendt / sorteret",
  "Returneret til leverandør",
  "Midlertidigt oplagret",
];
