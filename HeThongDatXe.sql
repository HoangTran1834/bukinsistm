SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `DiaDiem`;
DROP TABLE IF EXISTS `ChiTietDatXe`;
DROP TABLE IF EXISTS `DanhGia`;
DROP TABLE IF EXISTS `DatXe`;
DROP TABLE IF EXISTS `CaTaiXe`;
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
    `thoiGianDat` DATETIME NOT NULL,
    `maNhanVien` INT,
    `maCa` INT NOT NULL,
    `diemTra` INT NOT NULL,
    `diemDon` INT NOT NULL,
    `maTuyenDuong` INT NOT NULL,
    `trangThai` VARCHAR(50) NOT NULL,
    `ghiChu` TEXT,
    `yeuCauChungXe` BOOLEAN NOT NULL,
    PRIMARY KEY (`maDatXe`)
);

CREATE TABLE `DanhGia` (
    `maDatXe` INT NOT NULL,
    `diemSo` TINYINT NOT NULL,
    `binhLuan` TEXT,
    `ngayDanhGia` DATE NOT NULL,
    PRIMARY KEY (`maDatXe`)
);

CREATE TABLE `CaTaiXe` (
    `maCa` INT NOT NULL AUTO_INCREMENT,
    `maTaiXe` INT NOT NULL,
    `maXe` INT NOT NULL,
    `gioXuatPhat` TIME NOT NULL,
    `ngayXuatPhat` DATE NOT NULL,
    `diaDiemXuatPhat` VARCHAR(25) NOT NULL,
    PRIMARY KEY (`maCa`)
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
    `diemDon` VARCHAR(25) NOT NULL,
    `diemTra` VARCHAR(25) NOT NULL,
    `giaCuoc` DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (`maTuyenDuong`)
);

CREATE TABLE `ChiTietDatXe` (
    `maChiTiet` INT NOT NULL AUTO_INCREMENT,
    `maDatXe` INT NOT NULL,
    `maCa` INT NOT NULL,
    `tenKhach` VARCHAR(50) NOT NULL,
    `soDienThoaiKhach` VARCHAR(20) NOT NULL,
    `diemTra` INT NOT NULL,
    `diemDon` INT NOT NULL,
    `maTuyenDuong` INT NOT NULL,
    `trangThai` VARCHAR(50) NOT NULL,
    `ghiChu` TEXT,
    PRIMARY KEY (`maChiTiet`)
);

CREATE TABLE `DiaDiem` (
	`maDiaDiem` INTEGER NOT NULL,
	`tenDiaDiem` INTEGER NOT NULL,
	`viDo` INTEGER NOT NULL,
	`kinhDo` INTEGER NOT NULL,
	PRIMARY KEY (`maDiaDiem`)
);

-- FOREIGN KEYS
ALTER TABLE `NguoiDung` ADD FOREIGN KEY (`vaiTro`) REFERENCES `VaiTro`(`maVaiTro`);
ALTER TABLE `NhanVien` ADD FOREIGN KEY (`maNhanVien`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `TaiXe` ADD FOREIGN KEY (`maTaiXe`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maNhanVien`) REFERENCES `NhanVien`(`maNhanVien`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maNguoiDung`) REFERENCES `NguoiDung`(`maNguoiDung`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maCa`) REFERENCES `CaTaiXe`(`maCa`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`maTuyenDuong`) REFERENCES `TuyenDuong`(`maTuyenDuong`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`diemDon`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `DatXe` ADD FOREIGN KEY (`diemTra`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `DanhGia` ADD FOREIGN KEY (`maDatXe`) REFERENCES `DatXe`(`maDatXe`);
ALTER TABLE `CaTaiXe` ADD FOREIGN KEY (`maTaiXe`) REFERENCES `TaiXe`(`maTaiXe`);
ALTER TABLE `CaTaiXe` ADD FOREIGN KEY (`maXe`) REFERENCES `Xe`(`maXe`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maDatXe`) REFERENCES `DatXe`(`maDatXe`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maCa`) REFERENCES `CaTaiXe`(`maCa`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`maTuyenDuong`) REFERENCES `TuyenDuong`(`maTuyenDuong`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`diemTra`) REFERENCES `DiaDiem`(`maDiaDiem`);
ALTER TABLE `ChiTietDatXe` ADD FOREIGN KEY (`diemDon`) REFERENCES `DiaDiem`(`maDiaDiem`);


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

CREATE TRIGGER them_nguoi_dung_sau_khi_insert
AFTER INSERT ON NguoiDung
FOR EACH ROW
BEGIN
    IF NEW.vaiTro = 1 THEN
        INSERT INTO TaiXe(maTaiXe)
        VALUES (NEW.maNguoiDung);
        UPDATE NguoiDung SET is_staff = TRUE WHERE maNguoiDung = NEW.maNguoiDung;
    ELSEIF NEW.vaiTro = 2 THEN
        INSERT INTO NhanVien(maNhanVien, ngayVaoLam)
        VALUES (NEW.maNguoiDung, CURDATE());
        UPDATE NguoiDung SET is_staff = TRUE WHERE maNguoiDung = NEW.maNguoiDung;
    ELSEIF NEW.vaiTro = 0 THEN
        UPDATE NguoiDung SET is_staff = TRUE, is_superuser = TRUE WHERE maNguoiDung = NEW.maNguoiDung;
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
            INSERT INTO TaiXe(maTaiXe, cccd) VALUES (NEW.maNguoiDung, '');
        END IF;
        UPDATE NhanVien SET trangThai = 0 WHERE maNhanVien = NEW.maNguoiDung;
    -- Nếu vai trò thay đổi thành Nhân viên (2)
    ELSEIF NEW.vaiTro = 2 AND OLD.vaiTro <> 2 THEN
        IF EXISTS (SELECT 1 FROM NhanVien WHERE maNhanVien = NEW.maNguoiDung) THEN
            UPDATE NhanVien SET trangThai = 1 WHERE maNhanVien = NEW.maNguoiDung;
        ELSE
            INSERT INTO NhanVien(maNhanVien, ngayVaoLam, cccd) VALUES (NEW.maNguoiDung, CURDATE(), '');
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

INSERT INTO TuyenDuong (diemDon, diemTra, giaCuoc) VALUES
('Tam Kỳ', 'Đà Nẵng', 100000),
('Đà Nẵng', 'Thăng Bình', 80000),
('Tam Kỳ', 'Thăng Bình', 40000),
('Thăng Bình', 'Tam Kỳ', 40000),
('Thăng Bình', 'Đà Nẵng', 60000),
('Đà Nẵng', 'Tam Kỳ', 100000),
('Đà Nẵng', 'Quế Sơn', 70000),
('Quế Sơn', 'Đà Nẵng', 70000),
('Tam Kỳ', 'Quế Sơn', 60000),
('Quế Sơn', 'Tam Kỳ', 60000),
('Thăng Bình', 'Quế Sơn', 30000),
('Quế Sơn', 'Thăng Bình', 30000),
('Đà Nẵng', 'Điện Bàn', 20000),
('Điện Bàn', 'Đà Nẵng', 20000),
('Tam Kỳ', 'Điện Bàn', 90000),
('Điện Bàn', 'Tam Kỳ', 90000),
('Thăng Bình', 'Điện Bàn', 50000),
('Điện Bàn', 'Thăng Bình', 50000),
('Quế Sơn', 'Điện Bàn', 40000),
('Điện Bàn', 'Quế Sơn', 40000)


-- Lập lịch xe chạy tuyến Tam Kỳ <-> Đà Nẵng từ 5h đến 15h (Tam Kỳ) và 7h đến 17h (Đà Nẵng)
-- Phân bổ tài xế và xe hợp lý hơn: 
-- - Tài xế 2, 7 xuất phát sớm (5h, 6h, 7h)
-- - Tài xế 8, 9 xuất phát muộn (từ 8h trở đi)
-- - Tài xế 3, 4 không chạy chuyến 5h, 6h (chỉ từ 7h trở đi)
-- - Tài xế 5, 6 chỉ chạy chiều Đà Nẵng về Tam Kỳ, không chạy Tam Kỳ đi Đà Nẵng
-- - 5 xe (1-5) chạy liên tục, xe 6,7,8 nghỉ trưa (delay từ 11h-13h)

-- Tam Kỳ đi Đà Nẵng: xuất phát từ 5h đến 15h
INSERT INTO CaTaiXe (maTaiXe, maXe, gioXuatPhat, ngayXuatPhat, diaDiemXuatPhat) VALUES
-- 5h, 6h: chỉ tài xế 2, 7, 8, 9, xe 1-4
(2, 1, '05:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '05:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '05:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '05:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '06:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '06:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '06:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '06:00:00', '2024-05-02', 'Tam Kỳ'),

-- 7h: thêm tài xế 3, 4, xe 5
(2, 1, '07:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '07:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '07:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '07:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '07:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 1, '07:00:00', '2024-05-02', 'Tam Kỳ'),

-- 8h-10h: tài xế 2,7,8,9,3,4, xe 1-6
(2, 1, '08:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '08:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '08:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '08:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '08:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 6, '08:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '09:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '09:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '09:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '09:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '09:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 6, '09:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '10:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '10:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '10:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '10:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '10:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 6, '10:00:00', '2024-05-02', 'Tam Kỳ'),

-- 11h-13h: chỉ xe 1-5 chạy, xe 6,7,8 nghỉ trưa
(2, 1, '11:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '11:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '11:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '11:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '11:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '12:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '12:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '12:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '12:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '12:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '13:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '13:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '13:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '13:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '13:00:00', '2024-05-02', 'Tam Kỳ'),

-- 14h-15h: tài xế 2,7,8,9,3,4, xe 1-6 quay lại chạy
(2, 1, '14:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '14:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '14:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '14:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '14:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 6, '14:00:00', '2024-05-02', 'Tam Kỳ'),

(2, 1, '15:00:00', '2024-05-02', 'Tam Kỳ'),
(7, 2, '15:00:00', '2024-05-02', 'Tam Kỳ'),
(8, 3, '15:00:00', '2024-05-02', 'Tam Kỳ'),
(9, 4, '15:00:00', '2024-05-02', 'Tam Kỳ'),
(3, 5, '15:00:00', '2024-05-02', 'Tam Kỳ'),
(4, 6, '15:00:00', '2024-05-02', 'Tam Kỳ'),

-- Đà Nẵng về Tam Kỳ: xuất phát từ 7h đến 17h
-- Tài xế 5,6 chủ yếu chạy chiều này, các tài xế khác luân phiên, xe 1-6, xe 7,8 nghỉ trưa
(5, 1, '07:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '07:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '07:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '07:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '07:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '07:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '08:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '08:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '08:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '08:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '08:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '08:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '09:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '09:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '09:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '09:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '09:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '09:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '10:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '10:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '10:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '10:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '10:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '10:00:00', '2024-05-02', 'Đà Nẵng'),

-- 11h-13h: chỉ xe 1-5 chạy, xe 6,7,8 nghỉ trưa
(5, 1, '11:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '11:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '11:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '11:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '11:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '12:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '12:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '12:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '12:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '12:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '13:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '13:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '13:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '13:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '13:00:00', '2024-05-02', 'Đà Nẵng'),

-- 14h-17h: xe 1-6, tài xế 5,6,2,7,8,9,3,4 luân phiên
(5, 1, '14:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '14:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '14:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '14:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '14:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '14:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '15:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '15:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '15:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '15:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '15:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '15:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '16:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '16:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '16:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '16:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '16:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '16:00:00', '2024-05-02', 'Đà Nẵng'),

(5, 1, '17:00:00', '2024-05-02', 'Đà Nẵng'),
(6, 2, '17:00:00', '2024-05-02', 'Đà Nẵng'),
(2, 3, '17:00:00', '2024-05-02', 'Đà Nẵng'),
(7, 4, '17:00:00', '2024-05-02', 'Đà Nẵng'),
(8, 5, '17:00:00', '2024-05-02', 'Đà Nẵng'),
(9, 6, '17:00:00', '2024-05-02', 'Đà Nẵng');
