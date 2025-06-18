SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `DiaDiem`;
DROP TABLE IF EXISTS `ChiTietDatXe`;
DROP TABLE IF EXISTS `DanhGia`;
DROP TABLE IF EXISTS `DatXe`;
DROP TABLE IF EXISTS `ChiTietCa`;
DROP TABLE IF EXISTS `Ca`;
DROP TABLE IF EXISTS `Huyen`;
DROP TABLE IF EXISTS `TaiXe`;
DROP TABLE IF EXISTS `NhanVien`;
DROP TABLE IF EXISTS `Xe`;
DROP TABLE IF EXISTS `TuyenDuong`;
DROP TABLE IF EXISTS `NguoiDung`;
DROP TABLE IF EXISTS `VaiTro`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `NguoiDung` (
    `maNguoiDung` INT NOT NULL AUTO_INCREMENT,
    `hoTen` VARCHAR(50) NOT NULL,
    `soDienThoai` VARCHAR(25) NOT NULL UNIQUE,
    `matKhau` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100),
    `vaiTro` INT NOT NULL,
    `ngayTao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Các trường để tương thích với Django
    `is_superuser` BOOLEAN NOT NULL DEFAULT FALSE,
    `is_staff` BOOLEAN NOT NULL DEFAULT FALSE,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `last_login` DATETIME,
    PRIMARY KEY (`maNguoiDung`)
);

CREATE TABLE `VaiTro` (
    `maVaiTro` INT NOT NULL,
    `tenVaiTro` VARCHAR(15) NOT NULL,
    PRIMARY KEY (`maVaiTro`)
);

CREATE TABLE `NhanVien` (
    `maNhanVien` INT NOT NULL,
    `ngayVaoLam` DATE NOT NULL,
    `cccd` VARCHAR(20),
    `trangThai` BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (`maNhanVien`)
);

CREATE TABLE `TaiXe` (
    `maTaiXe` INT NOT NULL,
    `cccd` VARCHAR(20),
    `trangThai` BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (`maTaiXe`)
);

CREATE TABLE `DatXe` (
    `maDatXe` INT NOT NULL AUTO_INCREMENT,
    `maNguoiDung` INT NOT NULL,
    `maCa` INT NOT NULL, -- mã ca để xác định giờ xuất phát và hướng di chuyển
    `thoiGianDat` DATETIME NULL DEFAULT CURRENT_TIMESTAMP, -- tự động set khi tạo booking
    `maNhanVien` INT,
    `maChiTietCa` INT NULL, -- đổi sang mã chi tiết ca, nullable
    `diemTra` INT NOT NULL,
    `diemDon` INT NOT NULL,
    `maTuyenDuong` INT NULL, -- nullable để bổ sung sau
    `trangThai` VARCHAR(50) NOT NULL,
    `ghiChu` TEXT,
    `soGhe` INT NOT NULL DEFAULT 1, -- thêm số ghế
    PRIMARY KEY (`maDatXe`)
);

CREATE TABLE `DanhGia` (
    `maDatXe` INT NOT NULL,
    `diemSo` TINYINT NOT NULL,
    `binhLuan` TEXT,
    `ngayDanhGia` DATE NOT NULL,
    PRIMARY KEY (`maDatXe`)
);

CREATE TABLE `Huyen` (
    `maHuyen` INT NOT NULL AUTO_INCREMENT,
    `tenHuyen` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`maHuyen`)
);

CREATE TABLE `Ca` (
    `maCa` INT NOT NULL AUTO_INCREMENT,
    `gioXuatPhat` TIME NOT NULL,
    `ngayXuatPhat` DATE NOT NULL,
    `maHuyenXuatPhat` INT NOT NULL,
    PRIMARY KEY (`maCa`)
);

CREATE TABLE `ChiTietCa` (
    `maChiTietCa` INT NOT NULL AUTO_INCREMENT,
    `maCa` INT NOT NULL,
    `maXe` INT NOT NULL,
    `maTaiXe` INT NOT NULL,
    PRIMARY KEY (`maChiTietCa`)
);

CREATE TABLE `Xe` (
    `maXe` INT NOT NULL AUTO_INCREMENT,
    `bienSoXe` VARCHAR(20) NOT NULL,
    `loaiXe` VARCHAR(50),
    `soChoNgoi` INT NOT NULL,
    PRIMARY KEY (`maXe`)
);

CREATE TABLE `TuyenDuong` (
    `maTuyenDuong` INT NOT NULL AUTO_INCREMENT,
    `huyenDon` INT NOT NULL,
    `huyenTra` INT NOT NULL,
    `giaCuoc` DECIMAL(10, 2) NOT NULL,
    `huongChay` INT NOT NULL DEFAULT 1 COMMENT '1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng',
    PRIMARY KEY (`maTuyenDuong`)
);

CREATE TABLE `ChiTietDatXe` (
    `maChiTiet` INT NOT NULL AUTO_INCREMENT,
    `maDatXe` INT NOT NULL,
    `maChiTietCa` INT NULL, -- đổi sang mã chi tiết ca, nullable
    `tenKhach` VARCHAR(50) NOT NULL,
    `soDienThoaiKhach` VARCHAR(20) NOT NULL,
    `diemTra` INT NOT NULL,
    `diemDon` INT NOT NULL,
    `maTuyenDuong` INT NULL, -- nullable để bổ sung sau
    `trangThai` VARCHAR(50) NOT NULL,
    `ghiChu` TEXT,
    `soGhe` INT NOT NULL DEFAULT 1, -- thêm số ghế
    PRIMARY KEY (`maChiTiet`)
);

CREATE TABLE `DiaDiem` (
	`maDiaDiem` INT NOT NULL AUTO_INCREMENT,
	`tenDiaDiem` VARCHAR(255) NOT NULL,
	`viDo` FLOAT NOT NULL,
	`kinhDo` FLOAT NOT NULL,
	PRIMARY KEY (`maDiaDiem`)
);

-- FOREIGN KEYS
ALTER TABLE `NguoiDung` ADD FOREIGN KEY (`vaiTro`) REFERENCES `VaiTro`(`maVaiTro`);
ALTER TABLE `NhanVien` ADD FOREIGN KEY (`maNhanVien`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `TaiXe` ADD FOREIGN KEY (`maTaiXe`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maNhanVien`) REFERENCES `NhanVien`(`maNhanVien`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maNguoiDung`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maCa`) REFERENCES `Ca`(`maCa`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maChiTietCa`) REFERENCES `ChiTietCa`(`maChiTietCa`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maTuyenDuong`) REFERENCES `TuyenDuong`(`maTuyenDuong`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`diemDon`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`diemTra`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `DanhGia` ADD FOREIGN KEY (`maDatXe`) REFERENCES `DatXe`(`maDatXe`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maDatXe`) REFERENCES `DatXe`(`maDatXe`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maChiTietCa`) REFERENCES `ChiTietCa`(`maChiTietCa`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maTuyenDuong`) REFERENCES `TuyenDuong`(`maTuyenDuong`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`diemTra`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`diemDon`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `Ca` ADD FOREIGN KEY (`maHuyenXuatPhat`) REFERENCES `Huyen`(`maHuyen`);
ALTER TABLE `ChiTietCa` ADD FOREIGN KEY (`maCa`) REFERENCES `Ca`(`maCa`);
ALTER TABLE `ChiTietCa` ADD FOREIGN KEY (`maXe`) REFERENCES `Xe`(`maXe`);
ALTER TABLE `ChiTietCa` ADD FOREIGN KEY (`maTaiXe`) REFERENCES `TaiXe`(`maTaiXe`);
ALTER TABLE `TuyenDuong` ADD FOREIGN KEY (`huyenDon`) REFERENCES `Huyen`(`maHuyen`);
ALTER TABLE `TuyenDuong` ADD FOREIGN KEY (`huyenTra`) REFERENCES `Huyen`(`maHuyen`);


-- TRIGGERS
DELIMITER //
CREATE TRIGGER xu_ly_trung_sdt_truoc_khi_insert
BEFORE INSERT ON NguoiDung
FOR EACH ROW
BEGIN
    DECLARE dem INT DEFAULT 1;
    DECLARE sdt_moi VARCHAR(30);
    IF EXISTS (SELECT 1 FROM NguoiDung WHERE soDienThoai = NEW.soDienThoai) THEN
        SET sdt_moi = CONCAT(NEW.soDienThoai, '-', dem);
        WHILE EXISTS (SELECT 1 FROM NguoiDung WHERE soDienThoai = sdt_moi) DO
            SET dem = dem + 1;
            SET sdt_moi = CONCAT(NEW.soDienThoai, '-', dem);
        END WHILE;
        UPDATE NguoiDung 
        SET soDienThoai = sdt_moi, trangThai = 0
        WHERE soDienThoai = NEW.soDienThoai;
    END IF;
END //

DELIMITER //
CREATE TRIGGER set_staff_superuser_truoc_khi_insert
BEFORE INSERT ON NguoiDung
FOR EACH ROW
BEGIN
    IF NEW.vaiTro = 1 THEN
        SET NEW.is_staff = TRUE;
        SET NEW.is_superuser = FALSE;
    ELSEIF NEW.vaiTro = 2 THEN
        SET NEW.is_staff = TRUE;
        SET NEW.is_superuser = FALSE;
    ELSEIF NEW.vaiTro = 0 THEN
        SET NEW.is_staff = TRUE;
        SET NEW.is_superuser = TRUE;
    ELSE
        SET NEW.is_staff = FALSE;
        SET NEW.is_superuser = FALSE;
    END IF;
END //

DELIMITER //
CREATE TRIGGER them_nguoi_dung_sau_khi_insert
AFTER INSERT ON NguoiDung
FOR EACH ROW
BEGIN
    IF NEW.vaiTro = 1 THEN
        INSERT INTO TaiXe(maTaiXe, cccd, trangThai)
        VALUES (NEW.maNguoiDung, '', 1);
    ELSEIF NEW.vaiTro = 2 THEN
        INSERT INTO NhanVien(maNhanVien, ngayVaoLam, cccd, trangThai)
        VALUES (NEW.maNguoiDung, CURDATE(), '', 1);
    END IF;
END //

DELIMITER ;

DELIMITER //
CREATE TRIGGER cap_nhat_vai_tro_nguoi_dung
AFTER UPDATE ON NguoiDung
FOR EACH ROW
BEGIN
    -- Nếu vai trò thay đổi thành Tài xế (1)
    IF NEW.vaiTro = 1 AND OLD.vaiTro <> 1 THEN
        IF EXISTS (SELECT 1 FROM TaiXe WHERE maTaiXe = NEW.maNguoiDung) THEN
            UPDATE TaiXe SET trangThai = 1 WHERE maTaiXe = NEW.maNguoiDung;
        ELSE
            INSERT INTO TaiXe(maTaiXe, cccd, trangThai) VALUES (NEW.maNguoiDung, '', 1);
        END IF;
        UPDATE NhanVien SET trangThai = 0 WHERE maNhanVien = NEW.maNguoiDung;
    -- Nếu vai trò thay đổi thành Nhân viên (2)
    ELSEIF NEW.vaiTro = 2 AND OLD.vaiTro <> 2 THEN
        IF EXISTS (SELECT 1 FROM NhanVien WHERE maNhanVien = NEW.maNguoiDung) THEN
            UPDATE NhanVien SET trangThai = 1 WHERE maNhanVien = NEW.maNguoiDung;
        ELSE
            INSERT INTO NhanVien(maNhanVien, ngayVaoLam, cccd, trangThai) VALUES (NEW.maNguoiDung, CURDATE(), '', 1);
        END IF;
        UPDATE TaiXe SET trangThai = 0 WHERE maTaiXe = NEW.maNguoiDung;
    -- Nếu vai trò thay đổi thành khác (không phải Tài xế hoặc Nhân viên)
    ELSEIF NEW.vaiTro NOT IN (1,2) AND OLD.vaiTro IN (1,2) THEN
        UPDATE TaiXe SET trangThai = 0 WHERE maTaiXe = NEW.maNguoiDung;
        UPDATE NhanVien SET trangThai = 0 WHERE maNhanVien = NEW.maNguoiDung;
    END IF;
END //

DELIMITER ;



-- INSERT DATA
INSERT INTO VaiTro (maVaiTro, tenVaiTro) VALUES
(0, 'Admin'),
(1, 'Tài xế'),
(2, 'Nhân viên'),
(3, 'Hành khách');

INSERT INTO NguoiDung (hoTen, soDienThoai, matKhau, email, vaiTro) VALUES
('Trần Thị Bình', '0987654321', 'securepass456', 'tranthibinh@gmail.com', 1),
('Nguyễn Văn Hùng', '0977000001', 'txpass1', 'hungtx@gmail.com', 1),
('Trần Quốc Toàn', '0977000002', 'txpass2', 'toantx@gmail.com', 1),
('Lê Văn Tám', '0977000003', 'txpass3', 'tamtv@gmail.com', 1),
('Phan Văn Cường', '0977000004', 'txpass4', 'cuongtx@gmail.com', 1),
('Nguyễn Thị Lan', '0977000005', 'txpass5', 'lantx@gmail.com', 1),
('Đỗ Văn Bình', '0977000006', 'txpass6', 'binhtx@gmail.com', 1),
('Trần Thị Mai', '0977000007', 'txpass7', 'maitx@gmail.com', 1),
('Lê Văn Dũng', '0977000008', 'txpass8', 'dungtx@gmail.com', 1),
('Lê Văn Chính', '0909090909', 'mypassword789', 'levanchinh@gmail.com', 2),
('Ngô Thị Hạnh', '0955555555', 'nhanvienpass', 'ngothihanh@gmail.com', 2),
('Nguyễn Văn An', '0912345678', 'password123', 'nguyenvanan@gmail.com', 3),
('Phạm Minh Đức', '0933123456', 'userpass321', 'phamminhduc@gmail.com', 3),
('Hoàng Thị Em', '0944987654', 'strongpass654', 'hoangthiem@gmail.com', 3),
('Đặng Văn Phúc', '0967894321', 'safe123pass', 'dangvanphuc@gmail.com', 3),
('Vũ Minh Tuấn', '0933555777', 'khachpass1', 'vuminhtuan@gmail.com', 3),
('Lý Thị Hoa', '0922444666', 'khachpass2', 'lythihoa@gmail.com', 3),
('Trịnh Văn Sơn', '0911222333', 'khachpass3', 'trinhvanson@gmail.com', 3),
('Nguyễn Thị Hồng', '0911000001', 'khachpass4', 'hongnguyen@gmail.com', 3),
('Phạm Văn Lộc', '0911000002', 'khachpass5', 'locpham@gmail.com', 3),
('Lê Thị Thu', '0911000003', 'khachpass6', 'thule@gmail.com', 3),
('Trần Văn Hòa', '0911000004', 'khachpass7', 'hoatran@gmail.com', 3),
('Đỗ Thị Mai', '0911000005', 'khachpass8', 'maido@gmail.com', 3),
('Ngô Văn Phước', '0911000006', 'khachpass9', 'phuocngo@gmail.com', 3),
('Bùi Thị Lan', '0911000007', 'khachpass10', 'lanbui@gmail.com', 3),
('Võ Văn Tài', '0911000008', 'khachpass11', 'taivo@gmail.com', 3),
('Phan Thị Cúc', '0911000009', 'khachpass12', 'cucphan@gmail.com', 3),
('Lương Văn Hạnh', '0911000010', 'khachpass13', 'hanhluong@gmail.com', 3),
('Trịnh Thị Hương', '0911000011', 'khachpass14', 'huongtrinh@gmail.com', 3),
('Đặng Văn Minh', '0911000012', 'khachpass15', 'minhdang@gmail.com', 3),
('Nguyễn Thị Yến', '0911000013', 'khachpass16', 'yennguyen@gmail.com', 3),
('Phạm Văn Quý', '0911000014', 'khachpass17', 'quypham@gmail.com', 3),
('Lê Thị Hòa', '0911000015', 'khachpass18', 'hoale@gmail.com', 3),
('Trần Văn Phước', '0911000016', 'khachpass19', 'phuoctran@gmail.com', 3),
('Nguyễn Thị Kim', '0911000017', 'khachpass20', 'kimnguyen@gmail.com', 3),
('Phạm Văn Hùng', '0911000018', 'khachpass21', 'hungpham@gmail.com', 3),
('Lê Thị Hạnh', '0911000019', 'khachpass22', 'hanhle@gmail.com', 3),
('Trần Văn Dũng', '0911000020', 'khachpass23', 'dungtran@gmail.com', 3),
('Đỗ Thị Hương', '0911000021', 'khachpass24', 'huongdo@gmail.com', 3),
('Ngô Văn Bình', '0911000022', 'khachpass25', 'binhngo@gmail.com', 3),
('Bùi Thị Mai', '0911000023', 'khachpass26', 'maibui@gmail.com', 3),
('Võ Văn Sơn', '0911000024', 'khachpass27', 'sonvo@gmail.com', 3);

-- Tạo tài khoản quản trị viên
-- Mật khẩu: admin123
INSERT INTO NguoiDung (hoTen, soDienThoai, matKhau, email, vaiTro, is_superuser, is_staff, is_active) VALUES
('Quản Trị Viên', '0123456789', 'admin123', 'admin@hcb.com', 0, TRUE, TRUE, TRUE);

INSERT INTO Xe (bienSoXe, loaiXe, soChoNgoi) VALUES
('51A-12345', '4 chỗ', 4),
('29B-67890', '4 chỗ', 4),
('43A-11111', '7 chỗ', 7),
('43B-22222', '7 chỗ', 7),
('43C-33333', '7 chỗ', 7),
('43D-44444', '7 chỗ', 7),
('43E-55555', '7 chỗ', 7),
('43F-66666', '7 chỗ', 7);

-- Thêm dữ liệu mẫu cho huyện trước khi insert tuyến đường
INSERT INTO Huyen (tenHuyen) VALUES
('Tam Kỳ'), -- 1
('Đà Nẵng'), -- 2
('Thăng Bình'), -- 3
('Quế Sơn'), -- 4
('Điện Bàn'); -- 5

-- Insert tuyến đường sau khi đã có huyện
INSERT INTO TuyenDuong (huyenDon, huyenTra, giaCuoc, huongChay) VALUES
(1, 2, 100000, 2), -- Tam Kỳ đi Đà Nẵng
(2, 3, 80000, 1), -- Đà Nẵng đi Thăng Bình
(1, 3, 40000, 2), -- Tam Kỳ đi Thăng Bình
(3, 1, 40000, 1), -- Thăng Bình đi Tam Kỳ
(3, 2, 60000, 1), -- Thăng Bình đi Đà Nẵng
(2, 1, 100000, 1), -- Đà Nẵng đi Tam Kỳ
(2, 4, 70000, 1), -- Đà Nẵng đi Quế Sơn
(4, 2, 70000, 2), -- Quế Sơn đi Đà Nẵng
(1, 4, 60000, 2), -- Tam Kỳ đi Quế Sơn
(4, 1, 60000, 1), -- Quế Sơn đi Tam Kỳ
(3, 4, 30000, 2), -- Thăng Bình đi Quế Sơn
(4, 3, 30000, 1), -- Quế Sơn đi Thăng Bình
(2, 5, 20000, 1), -- Đà Nẵng đi Điện Bàn
(5, 2, 20000, 2), -- Điện Bàn đi Đà Nẵng
(1, 5, 90000, 2), -- Tam Kỳ đi Điện Bàn
(5, 1, 90000, 1), -- Điện Bàn đi Tam Kỳ
(3, 5, 50000, 1), -- Thăng Bình đi Điện Bàn
(5, 3, 50000, 2), -- Điện Bàn đi Thăng Bình
(4, 5, 40000, 1), -- Quế Sơn đi Điện Bàn
(5, 4, 40000, 2); -- Điện Bàn đi Quế Sơn

-- Insert Ca trước, sau đó insert ChiTietCa dựa trên mã Ca vừa tạo
INSERT INTO Ca (gioXuatPhat, ngayXuatPhat, maHuyenXuatPhat) VALUES
('05:00:00', '2024-05-02', 1),
('06:00:00', '2024-05-02', 1),
('07:00:00', '2024-05-02', 1),
('08:00:00', '2024-05-02', 1),
('09:00:00', '2024-05-02', 1),
('10:00:00', '2024-05-02', 1),
('11:00:00', '2024-05-02', 1),
('12:00:00', '2024-05-02', 1),
('13:00:00', '2024-05-02', 1),
('14:00:00', '2024-05-02', 1),
('15:00:00', '2024-05-02', 1),
('07:00:00', '2024-05-02', 2),
('08:00:00', '2024-05-02', 2),
('09:00:00', '2024-05-02', 2),
('10:00:00', '2024-05-02', 2),
('11:00:00', '2024-05-02', 2),
('12:00:00', '2024-05-02', 2),
('13:00:00', '2024-05-02', 2),
('14:00:00', '2024-05-02', 2),
('15:00:00', '2024-05-02', 2),
('16:00:00', '2024-05-02', 2),
('17:00:00', '2024-05-02', 2);

-- Gán nhiều xe-tài xế cho mỗi ca đúng logic phân bổ
-- Tam Kỳ đi Đà Nẵng (Ca 1-11)
INSERT INTO ChiTietCa (maCa, maXe, maTaiXe) VALUES
-- 5h, 6h, 7h: tài xế 2, 7, 8, 9, xe 1-4
(1, 1, 2), (1, 2, 7), (1, 3, 8), (1, 4, 9),
(2, 1, 2), (2, 2, 7), (2, 3, 8), (2, 4, 9),
(3, 1, 2), (3, 2, 7), (3, 3, 8), (3, 4, 9), (3, 5, 3), (3, 6, 4),
-- 8h-10h: tài xế 2,7,8,9,3,4, xe 1-6
(4, 1, 2), (4, 2, 7), (4, 3, 8), (4, 4, 9), (4, 5, 3), (4, 6, 4),
(5, 1, 2), (5, 2, 7), (5, 3, 8), (5, 4, 9), (5, 5, 3), (5, 6, 4),
(6, 1, 2), (6, 2, 7), (6, 3, 8), (6, 4, 9), (6, 5, 3), (6, 6, 4),
-- 11h-13h: chỉ xe 1-5 chạy, xe 6,7,8 nghỉ trưa, tài xế 2,7,3,4
(7, 1, 2), (7, 2, 7), (7, 3, 3), (7, 4, 4), (7, 5, 3),
(8, 1, 2), (8, 2, 7), (8, 3, 3), (8, 4, 4), (8, 5, 3),
(9, 1, 2), (9, 2, 7), (9, 3, 3), (9, 4, 4), (9, 5, 3),
-- 14h-15h: tài xế 2,7,8,9,3,4, xe 1-6 quay lại chạy
(10, 1, 2), (10, 2, 7), (10, 3, 8), (10, 4, 9), (10, 5, 3), (10, 6, 4),
(11, 1, 2), (11, 2, 7), (11, 3, 8), (11, 4, 9), (11, 5, 3), (11, 6, 4);

-- Đà Nẵng về Tam Kỳ (Ca 12-22)
INSERT INTO ChiTietCa (maCa, maXe, maTaiXe) VALUES
-- 7h-10h: tài xế 5,6,2,7, xe 1-6
(12, 1, 5), (12, 2, 6), (12, 3, 2), (12, 4, 7), (12, 5, 5), (12, 6, 6),
(13, 1, 5), (13, 2, 6), (13, 3, 2), (13, 4, 7), (13, 5, 5), (13, 6, 6),
(14, 1, 5), (14, 2, 6), (14, 3, 2), (14, 4, 7), (14, 5, 5), (14, 6, 6),
(15, 1, 5), (15, 2, 6), (15, 3, 2), (15, 4, 7), (15, 5, 5), (15, 6, 6),
-- 11h-13h: chỉ xe 1-5 chạy, xe 6,7,8 nghỉ trưa, tài xế 5,6,2,7
(16, 1, 5), (16, 2, 6), (16, 3, 2), (16, 4, 7), (16, 5, 5),
(17, 1, 5), (17, 2, 6), (17, 3, 2), (17, 4, 7), (17, 5, 5),
(18, 1, 5), (18, 2, 6), (18, 3, 2), (18, 4, 7), (18, 5, 5),
-- 14h-17h: xe 1-6, tài xế 5,6,2,7,8,9,3,4 luân phiên
(19, 1, 5), (19, 2, 6), (19, 3, 2), (19, 4, 7), (19, 5, 8), (19, 6, 9),
(20, 1, 3), (20, 2, 4), (20, 3, 5), (20, 4, 6), (20, 5, 2), (20, 6, 7),
(21, 1, 8), (21, 2, 9), (21, 3, 3), (21, 4, 4), (21, 5, 5), (21, 6, 6),
(22, 1, 2), (22, 2, 7), (22, 3, 8), (22, 4, 9), (22, 5, 3), (22, 6, 4);

-- Thêm dữ liệu địa điểm mẫu với tọa độ thực tế (float)
INSERT INTO DiaDiem (tenDiaDiem, viDo, kinhDo) VALUES
('123 Lê Lợi, Tam Kỳ', 15.5700, 108.4800),
('45 Nguyễn Văn Linh, Đà Nẵng', 16.0544, 108.2022),
('12 Trần Phú, Thăng Bình', 15.6000, 108.4500),
('88 Hùng Vương, Quế Sơn', 15.5500, 108.5000),
('99 Lý Thường Kiệt, Điện Bàn', 15.9800, 108.2500);

-- -- Thêm dữ liệu đặt xe
-- INSERT INTO DatXe (maNguoiDung, thoiGianDat, maNhanVien, maChiTietCa, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu, soGhe) VALUES
-- (12, '2024-05-01 10:00:00', 10, 1, 2, 1, 1, 'Đã xác nhận', 'Khách cần ghế trẻ em', 0),
-- (13, '2024-05-01 11:00:00', 11, 2, 1, 2, 2, 'Đã xác nhận', '', 1),
-- (14, '2024-05-01 12:00:00', 10, 3, 2, 1, 1, 'Chờ xác nhận', '', 0),
-- (15, '2024-05-01 13:00:00', 11, 4, 1, 2, 2, 'Đã hủy', 'Khách hủy do thay đổi lịch', 0),
-- (16, '2024-05-01 14:00:00', 10, 5, 2, 1, 1, 'Đã xác nhận', '', 1),
-- (17, '2024-05-01 15:00:00', 10, 6, 2, 1, 1, 'Đã xác nhận', '', 0);

-- -- Thêm dữ liệu chi tiết đặt xe
-- -- Đặt xe 1: 1 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (1, 1, 'Nguyễn Văn An', '0912345678', 2, 1, 1, 'Đã xác nhận', '');

-- -- Đặt xe 2: 2 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (2, 2, 'Phạm Minh Đức', '0933123456', 1, 2, 2, 'Đã xác nhận', 'Yêu cầu xe rộng'),
-- (2, 2, 'Nguyễn Thị Lan', '0977000005', 1, 2, 2, 'Đã xác nhận', '');

-- -- Đặt xe 3: 1 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (3, 3, 'Hoàng Thị Em', '0944987654', 2, 1, 1, 'Chờ xác nhận', '');

-- -- Đặt xe 4: 2 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (4, 4, 'Đặng Văn Phúc', '0967894321', 1, 2, 2, 'Đã hủy', 'Khách hủy'),
-- (4, 4, 'Lê Thị Thu', '0911000003', 1, 2, 2, 'Đã hủy', '');

-- -- Đặt xe 5: 1 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (5, 5, 'Vũ Minh Tuấn', '0933555777', 2, 1, 1, 'Đã xác nhận', '');

-- -- Đặt xe 6: 2 chi tiết
-- INSERT INTO ChiTietDatXe (maDatXe, maChiTietCa, tenKhach, soDienThoaiKhach, diemTra, diemDon, maTuyenDuong, trangThai, ghiChu) VALUES
-- (6, 6, 'Lý Thị Hoa', '0922444666', 2, 1, 1, 'Đã xác nhận', ''),
-- (6, 6, 'Trịnh Văn Sơn', '0911222333', 2, 1, 1, 'Đã xác nhận', '');
