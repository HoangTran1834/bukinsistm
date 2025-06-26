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
  manguoidung: number;
  vaitro: string;
  hoten: string;
  sodienthoai: string;
  password: string;
  email?: string;
  date_joined: string;
  is_active: boolean;
  is_staff: boolean;
  last_login: string | null;
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

export interface BookingResponse {
  madatxe: number;
  chitietdatxe: {
    machitiet: number;
    diemdon: DiaDiem;
    diemtra: DiaDiem;
    matuyenduong: string;
    machitietca: {
      machitietca: number;
      maca: Ca;
      maxe: {
        maxe: number;
        biensoxe: string;
        loaixe: string;
        sochongoi: number;
      };
      mataixe: {
        mataixe: number;
        hoten: string;
        sodienthoai: string;
        cccd: string;
        trangthai: number;
      };
    };
    tenkhach: string;
    sodienthoaikhach: string;
    trangthai: string;
    ghichu: string;
    soghe: number;
    madatxe: number;
  }[];
  diemdon: DiaDiem;
  diemtra: DiaDiem;
  maca: Ca;
  machitietca: {
    machitietca: number;
    maca: Ca;
    maxe: {
      maxe: number;
      biensoxe: string;
      loaixe: string;
      sochongoi: number;
    };
    mataixe: {
      mataixe: number;
      hoten: string;
      sodienthoai: string;
      cccd: string;
      trangthai: number;
    };
  };
  manguoidung: UserResponse;
  thoigiandat: string;
  trangthai: string;
  ghichu: string;
  soghe: number;
  manhanvien: number;
  matuyenduong: number;
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
  getUserById: async (manguoidung: number): Promise<UserResponse> => {
    const response = await axios.get(`/user/${manguoidung}/`);
    return response.data;
  },
  getUserByPhone: async (sodienthoai: string): Promise<UserResponse | null> => {
    try {
      const response = await axios.get('/user/');
      const allUsers = response.data;
      
      // Filter users to find matching phone number
      let userList = [];
      if (Array.isArray(allUsers)) {
        userList = allUsers;
      } else if (allUsers && Array.isArray(allUsers.data)) {
        userList = allUsers.data;
      } else if (allUsers && Array.isArray(allUsers.results)) {
        userList = allUsers.results;
      }
      
      const foundUser = userList.find((user: UserResponse) => 
        user.sodienthoai === sodienthoai.trim()
      );
      
      return foundUser || null;
    } catch (error) {
      console.error('Error fetching users:', error);
      return null;
    }
  },  createUser: async (data: { hoten: string; sodienthoai: string; password: string; email?: string }): Promise<UserResponse> => {
    // Use existing signup API
    const signupResponse = await axios.post('/auth/signup/', {
      hoten: data.hoten,
      sodienthoai: data.sodienthoai,
      password: data.password,
      email: data.email || ''
    });
    
    // After successful signup, get the user by phone to return UserResponse
    const newUser = await api.getUserByPhone(data.sodienthoai);
    if (!newUser) {
      throw new Error('Failed to retrieve created user');
    }
    
    return newUser;
  },

  // Bookings
  createBooking: async (data: BookingRequest): Promise<BookingResponse> => {
    const response = await axios.post('/booking/', data);
    return response.data;
  },
  
  // Staff booking - nhân viên tạo booking cho khách hàng
  createStaffBooking: async (data: BookingRequest & { ma_khach: number; ma_nhanvien?: number }): Promise<BookingResponse> => {
    const response = await axios.post('/booking/staff/', data);
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
  updateBookingStatus: async (madatxe: number, data: { trangthai: string; ghichu?: string; soghe?: number; manhanvien?: number; matuyenduong?: number }) => {
    const response = await axios.put(`/booking/${madatxe}/`, data);
    return response.data;
  },  updateBookingDetailStatus: async (machitiet: number, data: { trangthai: string; ghichu?: string }) => {
    const response = await axios.put(`/booking/detail/${machitiet}/`, data);
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
  // Get booking price
  getBookingPrice: async (data: {
    lat_don: string;
    lon_don: string;
    lat_tra: string;
    lon_tra: string;
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
  getShifts: async (params?: { ngayxuatphat?: string; mahuyenxuatphat?: number }) => {
    const response = await axios.get('/shift/', { params });
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
    // Assign driver and vehicle to shift
  assignToShift: async (maca: number, data: { maxe: number; mataixe: number }) => {
    const response = await axios.post(`/shift/${maca}/chitiet/`, data);
    return response.data;
  },
  
  // Get shift details (chi tiết ca)
  getShiftDetails: async (maca: number) => {
    const response = await axios.get(`/shift/${maca}/chitiet/`);
    return response.data;
  },
  
  // Delete shift detail (xóa chi tiết ca)
  deleteShiftDetail: async (maca: number, chitietca_id: number) => {
    const response = await axios.delete(`/shift/${maca}/chitiet/`, {
      data: { chitietca_id }
    });
    return response.data;
  },
  
  // Delete shift (xóa ca)
  deleteShift: async (maca: number) => {
    const response = await axios.delete(`/shift/${maca}/`);
    return response.data;
  },
  
  // Get drivers list
  getDrivers: async () => {
    const response = await axios.get('/shift/taixe/');
    return response.data;
  },
  
  // Get vehicles list
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
  },

  // Get booking price details with distance and price breakdown
  getBookingPriceDetails: async (data: {
    lat_don: string;
    lon_don: string;
    lat_tra: string;
    lon_tra: string;
    soghe?: number;
  }) => {
    const response = await axios.post('/route/get_price/', data);
    return response.data;
  },
};

export default api;
