import axios from '@/services/axios.customize';

export interface LoginRequest {
  sodienthoai: string;
  password: string;
}

export interface SignupRequest {
  hoten: string;
  sodienthoai: string;
  password: string;
  email?: string;
}

export interface UserResponse {
  maNguoiDung: number;
  hoTen: string;
  sodienthoai: string;
  vaitro: string;
  email?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user?: UserResponse;
}

export interface BookingRequest {
  maca: number;
  diemdon: number;
  diemtra: number;
  soghe: number;
  ghichu?: string;
  chitietdatxe?: {
    tenkhach: string;
    sodienthoaikhach: string;
    diemdon?: number;
    diemtra?: number;
    soghe: number;
    ghichu?: string;
  }[];
}

export interface TuyenDuong {
  matuyenduong: number;
  tentuyenduong: string;
  giacuoc: number;
  huyendon: { mahuyen: number; tenhuyen: string };
  huyentra: { mahuyen: number; tenhuyen: string };
}

export interface DiaDiem {
  madiadiem: number;
  tendiadiem: string;
  vido: number;
  kinhdo: number;
}

export interface Ca {
  maca: number;
  gioxuatphat: string;
  ngayxuatphat: string;
  mahuyenxuatphat: {
    mahuyen: number;
    tenhuyen: string;
  };
}

const api = {
  // Authentication
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await axios.post('/auth/login/', data);
    return response.data;
  },
  
  signup: async (data: SignupRequest): Promise<{ message: string }> => {
    const response = await axios.post('/auth/signup/', data);
    return response.data;
  },
  
  logout: async (refreshToken: string): Promise<{ detail: string }> => {
    const response = await axios.post('/auth/logout/', { refresh: refreshToken });
    return response.data;
  },

  // User management
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await axios.get('/user/profile/');
    return response.data;
  },

  // Bookings
  createBooking: async (data: BookingRequest) => {
    const response = await axios.post('/booking/', data);
    return response.data;
  },
  
  getBookings: async () => {
    const response = await axios.get('/booking/');
    return response.data;
  },
  
  getBookingDetails: async (id: number) => {
    const response = await axios.get(`/booking/${id}/`);
    return response.data;
  },

  // Locations
  getLocations: async (): Promise<DiaDiem[]> => {
    const response = await axios.get('/booking/locations/');
    return response.data;
  },
  
  createLocation: async (data: { tendiadiem: string; lat: number; lon: number }) => {
    const response = await axios.post('/booking/create_location/', data);
    return response.data;
  },

  // Routes
  calculatePrice: async (data: {
    lat_don?: string;
    lon_don?: string;
    lat_tra?: string;
    lon_tra?: string;
    diachi_don?: string;
    diachi_tra?: string;
  }) => {
    const response = await axios.post('/route/get_price/', data);
    return response.data;
  },
  
  getTuyenDuong: async (data: {
    lat_don: string;
    lon_don: string;
    lat_tra: string;
    lon_tra: string;
  }) => {
    const response = await axios.post('/route/get_tuyen_duong/', data);
    return response.data;
  },

  // Shifts
  getShifts: async () => {
    const response = await axios.get('/shift/');
    return response.data;
  },
  
  createShift: async (data: {
    gioxuatphat: string;
    ngayxuatphat: string;
    mahuyenxuatphat_id: number;
  }) => {
    const response = await axios.post('/shift/', data);
    return response.data;
  },
  
  getShiftsByCa: async (data: {
    ngay: string;
    huyen_xuatphat?: number;
  }) => {
    const response = await axios.post('/booking/get_ca_by_date/', data);
    return response.data;
  },
  
  assignDriversForShift: async (ca_id: number) => {
    const response = await axios.post('/route/assign_driver_for_shift/', { ca_id });
    return response.data;
  },
  
  // Drivers and vehicles
  getDrivers: async () => {
    const response = await axios.get('/shift/taixe/');
    return response.data;
  },
  
  getVehicles: async () => {
    const response = await axios.get('/shift/xe/');
    return response.data;
  },
  
  // Map services
  searchAddress: async (query: string) => {
    const response = await axios.post('/route/search_address/', { query });
    return response.data;
  },
  
  reverseGeocode: async (lat: string, lon: string) => {
    const response = await axios.post('/route/reverse_geocode/', { lat, lon });
    return response.data;
  }
};

export default api;
