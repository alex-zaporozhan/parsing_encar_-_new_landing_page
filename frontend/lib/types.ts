export type VehicleDTO = {
  id: number;
  make: string;
  model: string;
  year: number;
  mileage_km: number | null;
  price: { amount: number; currency: string };
  photos: string[];
  source_url: string;
};

export type VehiclesResponse = {
  items: VehicleDTO[];
  total: number;
};
