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
    `soDienThoai` VARCHAR(15) NOT NULL,
    `matKhau` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100),
    `vaiTro` INT NOT NULL,
    `trangThai` BOOLEAN NOT NULL DEFAULT TRUE,
    `ngayTao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    `cccd` VARCHAR(20) NOT NULL,
    `trangThai` BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (`maNhanVien`)
);

CREATE TABLE `TaiXe` (
    `maTaiXe` INT NOT NULL,
    `cccd` VARCHAR(20) NOT NULL,
    `trangThai` BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (`maTaiXe`)
);

CREATE TABLE `DatXe` (
    `maDatXe` INT NOT NULL AUTO_INCREMENT,
    `maHanhKhach` INT NOT NULL,
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
    `soDienThoaiKhach` VARCHAR(15) NOT NULL,
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

CREATE TRIGGER them_nguoi_dung_sau_khi_insert
AFTER INSERT ON NguoiDung
FOR EACH ROW
BEGIN
    IF IF NEW.vaiTro = 1 THEN
        INSERT INTO TaiXe(maTaiXe, cccd)
        VALUES (NEW.maNguoiDung, ''); 
    ELSEIF NEW.vaiTro = 2 THEN
        INSERT INTO NhanVien(maNhanVien)
        VALUES (NEW.maNguoiDung);
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
('Nguyễn Văn An', '0912345678', 'password123', 'nguyenvanan@gmail.com', 3),
('Trần Thị Bình', '0987654321', 'securepass456', 'tranthibinh@gmail.com', 1),
('Lê Văn Chính', '0909090909', 'mypassword789', 'levanchinh@gmail.com', 2),
('Quản Trị Viên', '0123456789', 'adminsecure123', 'admin@hethongdatxe.com', 0),
('Phạm Minh Đức', '0933123456', 'userpass321', 'phamminhduc@gmail.com', 3),
('Hoàng Thị Em', '0944987654', 'strongpass654', 'hoangthiem@gmail.com', 3),
('Đặng Văn Phúc', '0967894321', 'safe123pass', 'dangvanphuc@gmail.com', 3);

INSERT INTO Xe (bienSoXe, loaiXe, soChoNgoi) VALUES
('51A-12345', '4 chỗ', 4),
('29B-67890', '7 chỗ', 7);

