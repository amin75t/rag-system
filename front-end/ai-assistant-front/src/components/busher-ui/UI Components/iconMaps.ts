import {
  IconPopulation,
  IconArea,
  IconUnemployment,
  IconGdp,
  IconCoast,
  IconEnergy,
  IconSea,
  IconIndustry,
} from "./Icons";

export const kpiIconMap: Record<string, React.FC<{ className?: string }>> = {
  population: IconPopulation,
  area: IconArea,
  unemployment: IconUnemployment,
  gdp: IconGdp,
  coast: IconCoast,
};

export const priorityIconMap: Record<string, React.FC<{ className?: string }>> = {
  energy: IconEnergy,
  sea: IconSea,
  industry: IconIndustry,
};