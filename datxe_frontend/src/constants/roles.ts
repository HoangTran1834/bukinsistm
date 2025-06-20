// User role constants that correspond to database values
export enum UserRole {
  ADMIN = "Admin",
  DRIVER = "Tài xế",
  STAFF = "Nhân viên",
  PASSENGER = "Hành khách"
}

export const roleToNumber = {
  [UserRole.ADMIN]: 0,
  [UserRole.DRIVER]: 1,
  [UserRole.STAFF]: 2,
  [UserRole.PASSENGER]: 3
};

export const numberToRole = {
  0: UserRole.ADMIN,
  1: UserRole.DRIVER,
  2: UserRole.STAFF,
  3: UserRole.PASSENGER
};

export const isAdmin = (role: string): boolean => {
  return role === UserRole.ADMIN;
};

export const isStaff = (role: string): boolean => {
  return role === UserRole.STAFF || role === UserRole.ADMIN;
};

export const isDriver = (role: string): boolean => {
  return role === UserRole.DRIVER;
};

export const isPassenger = (role: string): boolean => {
  return role === UserRole.PASSENGER;
};

// Helper function to check if user is hanh khach
export const isHanhKhach = (roleValue: UserRole): boolean => {
  return roleValue === UserRole.PASSENGER;
};
