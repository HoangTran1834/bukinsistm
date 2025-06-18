// User role constants that correspond to database values
export const USER_ROLES = {
  ADMIN: 0,
  TAI_XE: 1,
  NHAN_VIEN: 2,
  HANH_KHACH: 3,
};

// Role names for display purposes
export const ROLE_NAMES = {
  [USER_ROLES.ADMIN]: "Admin",
  [USER_ROLES.TAI_XE]: "Tài xế",
  [USER_ROLES.NHAN_VIEN]: "Nhân viên",
  [USER_ROLES.HANH_KHACH]: "Hành khách",
};

// Helper function to get role name by value
export const getRoleName = (roleValue) => {
  return ROLE_NAMES[roleValue] || "Không xác định";
};

// Helper function to check if user has admin privileges
export const isAdmin = (roleValue) => {
  return roleValue === USER_ROLES.ADMIN;
};

// Helper function to check if user is nhan vien
export const isNhanVien = (roleValue) => {
  return roleValue === USER_ROLES.NHAN_VIEN;
};

// Helper function to check if user is tai xe
export const isTaiXe = (roleValue) => {
  return roleValue === USER_ROLES.TAI_XE;
};

// Helper function to check if user is hanh khach
export const isHanhKhach = (roleValue) => {
  return roleValue === USER_ROLES.HANH_KHACH;
};
