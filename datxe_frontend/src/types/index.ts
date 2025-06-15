export interface User {
  manguoidung: number;
  hoten: string;
  sodienthoai: string;
  email?: string;
  vaitro: number;
  date_joined: string;
  is_active: boolean;
  is_staff: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  sodienthoai: string;
  password: string;
}

export interface SignupData {
  hoten: string;
  sodienthoai: string;
  password: string;
  email?: string;
}

export interface Shift {
  maca: number;
  mataixe: number;
  maxe: number;
  gioxuatphat: string;
  ngayxuatphat: string;
  diadiemxuatphat: string;
}

export interface BookingDetail {
  machitiet: number;
  madatxe: number;
  maca: number;
  tenkhach: string;
  sodienthoaikhach: string;
  diemtra: number;
  diemdon: number;
  matuyenduong: number;
  trangthai: string;
  ghichu?: string;
}

export interface Booking {
  madatxe: number;
  manguoidung: number;
  thoigiandat: string;
  manhanvien?: number;
  maca: number;
  diemtra: number;
  diemdon: number;
  matuyenduong: number;
  trangthai: string;
  ghichu?: string;
  yeucauchungxe: number;
  chitietdatxe?: BookingDetail[];
}

export enum UserRole {
  Admin = 0,
  Driver = 1,
  Staff = 2,
  Passenger = 3
}
  tenkhach?: string;
  sodienthoaikhach?: string;
}

export interface Shift {
  maca: number;
  mataixe: number;
  maxe: number;
  gioxuatphat: string;
  ngayxuatphat: string;
  diadiemxuatphat: string;
}

export interface Location {
  madiadiem: number;
  tendiadiem: string;
  vido: number;
  kinhdo: number;
}

export interface Route {
  matuyenduong: number;
  diemdon: string;
  diemtra: string;
  giacuoc: number;
}

export interface Vehicle {
  maxe: number;
  biensoxe: string;
  loaixe: string | null;
  sochongoi: number;
}
