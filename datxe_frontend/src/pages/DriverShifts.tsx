import React, { useState, useEffect } from 'react';
import {
  Card,
  DatePicker,
  Table,
  Spin,
  message,
  Typography,
  Space,
  Tag,
  Collapse,
  Divider,
  Row,
  Col,
  Alert,
  Button
} from 'antd';
import {
  CalendarOutlined,
  CarOutlined,
  UserOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../api/backend';

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface ChiTietCa {
  machitietca: number;
  maca: number;
  taixe_info: {
    mataixe: number;
    hoten: string;
    sodienthoai: string;
    email?: string;
    cccd?: string;
  };
  xe_info: {
    maxe: number;
    biensoxe: string;
    loaixe: string;
    sochongoi: number;
  };
}

interface Booking {
  madatxe: number;
  maca: number | {
    maca: number;
    mahuyenxuatphat: {
      mahuyen: number;
      tenhuyen: string;
    };
    gioxuatphat: string;
    ngayxuatphat: string;
  } | null;
  machitietca: number | {
    machitietca: number;
    maca: {
      maca: number;
      mahuyenxuatphat: {
        mahuyen: number;
        tenhuyen: string;
      };
      gioxuatphat: string;
      ngayxuatphat: string;
    };
    mataixe: {
      mataixe: number;
      hoten: string;
      sodienthoai: string;
      cccd?: string;
      trangthai: number;
    };
    maxe: {
      maxe: number;
      biensoxe: string;
      loaixe: string;
      sochongoi: number;
    };
  } | null;
  manguoidung: {
    manguoidung: number;
    vaitro: string;
    hoten: string;
    sodienthoai: string;
    email?: string;
    date_joined: string;
    is_active: boolean;
    is_staff: boolean;
    last_login: string | null;
    password: string;
  };
  hoten: string;
  sodienthoai: string;
  diemdon: {
    madiadiem: number;
    tendiadiem: string;
    vido: number;
    kinhdo: number;
  };
  diemtra: {
    madiadiem: number;
    tendiadiem: string;
    vido: number;
    kinhdo: number;  };
  soghe: number;
  ghichu?: string;
  trangthai?: string;
  chitietdatxe?: {
    tenkhach: string;
    sodienthoaikhach: string;
    diemdon?: {
      madiadiem: number;
      tendiadiem: string;
      vido: number;
      kinhdo: number;
    };
    diemtra?: {
      madiadiem: number;
      tendiadiem: string;
      vido: number;
      kinhdo: number;
    };
    soghe: number;
    ghichu?: string;
  }[];
}

interface Shift {
  maca: number;
  gioxuatphat: string;
  ngayxuatphat: string;
  mahuyenxuatphat: {
    mahuyen: number;
    tenhuyen: string;
  };
}

const DriverShifts: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [shiftDetails, setShiftDetails] = useState<ChiTietCa[]>([]);  const [bookings, setBookings] = useState<Record<number, Booking[]>>({});
  const [loading, setLoading] = useState(false);
  const [bookingLoading, setBookingLoading] = useState<Record<number, boolean>>({});
  const [loadedBookings, setLoadedBookings] = useState<Set<number>>(new Set());
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Load current user profile
  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        const user = await api.getCurrentUser();
        console.log('👤 Current user:', user);
        setCurrentUser(user);
      } catch (error) {
        console.error('❌ Error loading current user:', error);
        message.error('Không thể tải thông tin người dùng');
      }
    };
    
    loadCurrentUser();
  }, []);

  // Load shifts for selected date
  const loadShifts = async (date: dayjs.Dayjs) => {
    try {
      setLoading(true);
      const dateString = date.format('YYYY-MM-DD');
      console.log('🗓️ Loading shifts for date:', dateString);      const requestData = { "ngay": dateString };
      console.log('📤 Request data sent:', JSON.stringify(requestData));
      
      const response = await api.getShiftsByCa(requestData);
      
      console.log('📤 Request data sent:', { ngay: dateString });
      console.log('📋 Shifts response:', response);
      
      let shiftsData = [];
      if (Array.isArray(response)) {
        shiftsData = response;
      } else if (response && Array.isArray(response.data)) {
        shiftsData = response.data;
      } else if (response && Array.isArray(response.results)) {
        shiftsData = response.results;
      } else if (response && response.ca) {
        shiftsData = Array.isArray(response.ca) ? response.ca : [response.ca];
      }
      
      console.log('✅ Processed shifts:', shiftsData);
      setShifts(shiftsData);
        // Load shift details for each shift
      const allShiftDetails: ChiTietCa[] = [];
      for (const shift of shiftsData) {
        try {
          const details = await api.getShiftDetails(shift.maca);
          console.log(`📊 Shift ${shift.maca} details:`, details);
          
          let detailsArray = [];
          if (Array.isArray(details)) {
            detailsArray = details;
          } else if (details && Array.isArray(details.data)) {
            detailsArray = details.data;
          }
            // Filter only shift details for current driver
          if (currentUser && currentUser.manguoidung) {
            const driverShiftDetails = detailsArray.filter((detail: ChiTietCa) => {
              console.log('🔍 Checking detail:', detail.taixe_info?.mataixe, 'vs current user:', currentUser.manguoidung);
              return detail.taixe_info?.mataixe === currentUser.manguoidung;
            });
            
            console.log(`✅ Driver shift details for user ${currentUser.manguoidung}:`, driverShiftDetails);
            allShiftDetails.push(...driverShiftDetails);
          }
        } catch (error) {
          console.error(`❌ Error loading details for shift ${shift.maca}:`, error);
        }
      }
      
      console.log('🎯 Final filtered shift details:', allShiftDetails);
      setShiftDetails(allShiftDetails);
      
    } catch (error: any) {
      console.error('❌ Error loading shifts:', error);
      message.error('Không thể tải danh sách ca làm việc');
      setShifts([]);
      setShiftDetails([]);
    } finally {
      setLoading(false);
    }
  };  // Load bookings for a specific shift detail
  const loadBookings = async (chitietca: ChiTietCa) => {
    // Check if already loading or loaded
    if (bookingLoading[chitietca.machitietca] || loadedBookings.has(chitietca.machitietca)) {
      return;
    }
    
    try {
      setBookingLoading(prev => ({ ...prev, [chitietca.machitietca]: true }));
      setLoadedBookings(prev => new Set(prev).add(chitietca.machitietca));
      console.log('🎫 Loading bookings for shift detail:', chitietca.machitietca);console.log('🔍 Shift detail info:', {
        machitietca: chitietca.machitietca,
        maca: chitietca.maca,
        taixe: chitietca.taixe_info,
        selectedDate: selectedDate?.format('YYYY-MM-DD')
      });
      
      const response = await api.getBookings();
      console.log('📋 All bookings response:', response);
      
      // Filter bookings by maca and machitietca
      let allBookings = [];
      if (Array.isArray(response)) {
        allBookings = response;
      } else if (response && Array.isArray(response.data)) {
        allBookings = response.data;
      } else if (response && Array.isArray(response.results)) {
        allBookings = response.results;
      }
      
      console.log('📦 All bookings extracted:', allBookings);
      console.log('🔎 Filtering by maca:', chitietca.maca, 'and machitietca:', chitietca.machitietca);      const filteredBookings = allBookings.filter((booking: Booking) => {
        // Handle case where maca and machitietca might be objects, numbers, or null
        let bookingMaca = null;
        let bookingMachitietca = null;
        
        // Extract maca
        if (booking.maca) {
          bookingMaca = typeof booking.maca === 'object' ? booking.maca.maca : booking.maca;
        }
        
        // Extract machitietca
        if (booking.machitietca) {
          bookingMachitietca = typeof booking.machitietca === 'object' ? booking.machitietca.machitietca : booking.machitietca;
        }
        
        const matchesCa = bookingMaca === chitietca.maca;
        const matchesChitietCa = bookingMachitietca === chitietca.machitietca;
        
        console.log('🔍 Booking check:', {
          madatxe: booking.madatxe,
          booking_maca_raw: booking.maca,
          booking_machitietca_raw: booking.machitietca,
          booking_maca_extracted: bookingMaca,
          booking_machitietca_extracted: bookingMachitietca,
          target_maca: chitietca.maca,
          target_machitietca: chitietca.machitietca,
          matches_ca: matchesCa,
          matches_chitietca: matchesChitietCa,
          overall_match: matchesCa && matchesChitietCa
        });
        return matchesCa && matchesChitietCa;
      });
      
      console.log(`✅ Filtered bookings for shift detail ${chitietca.machitietca}:`, filteredBookings);
      
      setBookings(prev => ({
        ...prev,
        [chitietca.machitietca]: filteredBookings
      }));
      
    } catch (error: any) {
      console.error('❌ Error loading bookings:', error);
      message.error('Không thể tải danh sách hành khách');
    } finally {
      setBookingLoading(prev => ({ ...prev, [chitietca.machitietca]: false }));
    }
  };  // Update booking status
  const updateBookingStatus = async (madatxe: number, trangthai: string, chitietcaId: number) => {
    try {
      console.log(`🔄 Updating booking ${madatxe} status to: ${trangthai}`);
      
      await api.updateBookingStatus(madatxe, { trangthai });
      
      message.success(`Đã cập nhật trạng thái thành: ${trangthai}`);
      
      // Reload bookings for this shift detail to reflect changes
      const shiftDetail = shiftDetails.find(detail => detail.machitietca === chitietcaId);
      if (shiftDetail) {
        // Remove from loaded set to force reload
        setLoadedBookings(prev => {
          const newSet = new Set(prev);
          newSet.delete(chitietcaId);
          return newSet;
        });
        // Clear current bookings
        setBookings(prev => ({
          ...prev,
          [chitietcaId]: []
        }));
        // Reload
        await loadBookings(shiftDetail);
      }
      
    } catch (error: any) {
      console.error('❌ Error updating booking status:', error);
      message.error('Không thể cập nhật trạng thái đặt vé');
    }
  };

  // Handle date change
  const handleDateChange = (date: dayjs.Dayjs | null) => {
    setSelectedDate(date);
    setShifts([]);
    setShiftDetails([]);
    setBookings({});
    setLoadedBookings(new Set());
    if (date && currentUser) {
      loadShifts(date);
    }
  };
  // Columns for shift details table
  const shiftDetailColumns = [
    {
      title: 'Ca xe',
      dataIndex: 'maca',
      key: 'maca',
      render: (maca: number, record: ChiTietCa) => {
        const shift = shifts.find(s => s.maca === maca);
        return shift ? (
          <Space direction="vertical" size="small">
            <Text strong>Ca {maca}</Text>
            <Text type="secondary">{shift.gioxuatphat}</Text>
            <Text type="secondary">{shift.mahuyenxuatphat.tenhuyen}</Text>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              Chi tiết #{record.machitietca}
            </Text>
          </Space>
        ) : (
          <Space direction="vertical" size="small">
            <Text strong>Ca {maca}</Text>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              Chi tiết #{record.machitietca}
            </Text>
          </Space>
        );
      }
    },    {
      title: 'Tài xế',
      dataIndex: 'taixe_info',
      key: 'driver',
      render: (driver: any) => (
        <Space direction="vertical" size="small">
          <Text strong>{driver?.hoten || 'Chưa có thông tin'}</Text>
          <Text type="secondary">
            <PhoneOutlined /> {driver?.sodienthoai || 'N/A'}
          </Text>
        </Space>
      )
    },
    {
      title: 'Xe',
      dataIndex: 'xe_info',
      key: 'vehicle',
      render: (vehicle: any) => (
        <Space direction="vertical" size="small">
          <Text strong>{vehicle?.biensoxe || 'Chưa có thông tin'}</Text>
          <Tag color="blue">{vehicle?.sochongoi || 0} ghế</Tag>
        </Space>
      )
    },    {
      title: 'Hành khách',
      key: 'passengers',
      render: (_: any, record: ChiTietCa) => {
        const shiftBookings = bookings[record.machitietca] || [];
        // Calculate actual number of passengers (people), not seats
        const totalPassengers = shiftBookings.reduce((sum, booking) => {
          return sum + 1 + (booking.chitietdatxe?.length || 0); // Main booker + additional passengers
        }, 0);
        // Calculate total seats
        const totalSeats = shiftBookings.reduce((sum, booking) => {
          return sum + booking.soghe + (booking.chitietdatxe?.reduce((subSum, detail) => subSum + detail.soghe, 0) || 0);
        }, 0);
        
        return (
          <Space direction="vertical" size="small">
            <Tag color={totalPassengers > 0 ? 'green' : 'default'}>
              {totalPassengers} người
            </Tag>
            <Tag color={totalSeats > 0 ? 'blue' : 'default'}>
              {totalSeats} ghế
            </Tag>
            {!bookings[record.machitietca] && (
              <a onClick={() => loadBookings(record)}>
                {bookingLoading[record.machitietca] ? <Spin size="small" /> : 'Xem chi tiết'}
              </a>
            )}
          </Space>
        );
      }
    }
  ];
  // Render passenger details for a shift
  const renderPassengerDetails = (chitietca: ChiTietCa) => {
    const shiftBookings = bookings[chitietca.machitietca] || [];
    
    if (shiftBookings.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '24px' }}>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            Chưa có hành khách đặt vé cho ca này
          </Text>
        </div>
      );
    }

    // Calculate total passengers and seats
    const totalBookings = shiftBookings.length;
    const totalPassengers = shiftBookings.reduce((sum, booking) => {
      return sum + 1 + (booking.chitietdatxe?.length || 0); // Main booker + additional passengers
    }, 0);
    const totalSeats = shiftBookings.reduce((sum, booking) => {
      return sum + booking.soghe + (booking.chitietdatxe?.reduce((subSum, detail) => subSum + detail.soghe, 0) || 0);
    }, 0);

    return (
      <div style={{ backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px' }}>
        {/* Summary */}
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#fff', borderRadius: '6px', border: '1px solid #e8e8e8' }}>
          <Title level={5} style={{ margin: 0, marginBottom: '8px', color: '#1890ff' }}>
            📊 Tổng quan hành khách
          </Title>
          <Space size="large">
            <Tag color="green" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalBookings} đặt vé
            </Tag>
            <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalPassengers} hành khách
            </Tag>
            <Tag color="orange" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalSeats} ghế
            </Tag>
          </Space>
        </div>

        {/* Booking Details */}
        <div style={{ display: 'grid', gap: '12px' }}>
          {shiftBookings.map((booking, index) => {
            const additionalPassengers = booking.chitietdatxe || [];
            const totalPassengersInBooking = 1 + additionalPassengers.length;
            const totalSeatsInBooking = booking.soghe + additionalPassengers.reduce((sum, detail) => sum + detail.soghe, 0);
            
            return (
              <Card 
                key={booking.madatxe} 
                size="small" 
                style={{ 
                  marginBottom: '0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  border: '1px solid #e8e8e8'
                }}
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#1890ff', fontWeight: 'bold' }}>
                      🎫 Đặt vé #{booking.madatxe}
                    </span>
                    <Space>
                      <Tag color="cyan">{totalPassengersInBooking} người</Tag>
                      <Tag color="purple">{totalSeatsInBooking} ghế</Tag>
                    </Space>
                  </div>
                }
              >
                {/* Main booker */}
                <div style={{ 
                  marginBottom: additionalPassengers.length > 0 ? '16px' : '0', 
                  padding: '12px', 
                  backgroundColor: '#f6ffed', 
                  borderRadius: '6px',
                  border: '1px solid #b7eb8f'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                    <Text strong style={{ color: '#52c41a', fontSize: '14px' }}>
                      👤 Người đặt chính
                    </Text>
                  </div>
                    <Row gutter={[16, 8]}>
                    <Col xs={24} sm={12} md={8}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <UserOutlined style={{ color: '#52c41a' }} />
                        <Text strong>{booking?.manguoidung?.hoten || 'N/A'}</Text>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={8}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <PhoneOutlined style={{ color: '#1890ff' }} />
                        <Text>{booking?.manguoidung?.sodienthoai || 'N/A'}</Text>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={8}>
                      <Tag color="blue" style={{ fontSize: '13px' }}>
                        🪑 {booking?.soghe || 0} ghế
                      </Tag>
                    </Col>
                  </Row>
                  
                  <Row gutter={[16, 8]} style={{ marginTop: '8px' }}>
                    <Col xs={24} md={12}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <EnvironmentOutlined style={{ color: '#52c41a' }} />
                        <Text type="secondary">
                          <strong>Đón:</strong> {booking?.diemdon?.tendiadiem || 'Chưa có thông tin'}
                        </Text>
                      </div>
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                        <Text type="secondary">
                          <strong>Trả:</strong> {booking?.diemtra?.tendiadiem || 'Chưa có thông tin'}
                        </Text>
                      </div>
                    </Col>
                  </Row>
                    {booking?.ghichu && (
                    <div style={{ marginTop: '8px', padding: '6px 8px', backgroundColor: '#fff', borderRadius: '4px' }}>
                      <Text type="secondary" style={{ fontSize: '13px' }}>
                        💬 <strong>Ghi chú:</strong> {booking.ghichu}
                      </Text>
                    </div>
                  )}
                  
                  {/* Status and Action Buttons */}
                  <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#fff', borderRadius: '4px', border: '1px solid #e8e8e8' }}>
                    <Row gutter={[8, 8]} align="middle">
                      <Col>
                        <Text strong style={{ fontSize: '13px', color: '#666' }}>
                          Trạng thái:
                        </Text>
                      </Col>
                      <Col>
                        <Tag color={
                          booking?.trangthai === 'Đã đón' ? 'orange' :
                          booking?.trangthai === 'Đã trả' ? 'green' :
                          booking?.trangthai === 'Đã đặt' ? 'blue' : 'default'
                        }>
                          {booking?.trangthai || 'Chưa xác định'}
                        </Tag>
                      </Col>
                      <Col flex="auto" />
                      <Col>
                        <Space size="small">
                          <Button
                            size="small"
                            type="primary"
                            disabled={booking?.trangthai === 'Đã đón' || booking?.trangthai === 'Đã trả'}
                            onClick={() => updateBookingStatus(booking.madatxe, 'Đã đón', chitietca.machitietca)}
                          >
                            Đã đón
                          </Button>
                          <Button
                            size="small"
                            type="primary"
                            style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                            disabled={booking?.trangthai !== 'Đã đón'}
                            onClick={() => updateBookingStatus(booking.madatxe, 'Đã trả', chitietca.machitietca)}
                          >
                            Đã trả
                          </Button>
                        </Space>
                      </Col>
                    </Row>
                  </div>
                </div>

                {/* Additional passengers */}
                {additionalPassengers.length > 0 && (
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <Text strong style={{ color: '#1890ff', fontSize: '14px' }}>
                        👥 Hành khách bổ sung ({additionalPassengers.length})
                      </Text>
                    </div>
                    
                    <div style={{ display: 'grid', gap: '8px' }}>
                      {additionalPassengers.map((detail, detailIndex) => (
                        <div 
                          key={detailIndex} 
                          style={{ 
                            padding: '12px', 
                            backgroundColor: '#f0f5ff', 
                            borderRadius: '6px',
                            border: '1px solid #d6e4ff'
                          }}
                        >
                          <Row gutter={[16, 8]}>
                            <Col xs={24} sm={12} md={8}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <UserOutlined style={{ color: '#1890ff' }} />
                                <Text strong>{detail?.tenkhach || 'N/A'}</Text>
                              </div>
                            </Col>
                            <Col xs={24} sm={12} md={8}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <PhoneOutlined style={{ color: '#1890ff' }} />
                                <Text>{detail?.sodienthoaikhach || 'N/A'}</Text>
                              </div>
                            </Col>
                            <Col xs={24} sm={12} md={8}>
                              <Tag color="blue" style={{ fontSize: '13px' }}>
                                🪑 {detail?.soghe || 0} ghế
                              </Tag>
                            </Col>
                          </Row>
                          
                          {(detail?.diemdon || detail?.diemtra) && (
                            <Row gutter={[16, 8]} style={{ marginTop: '8px' }}>
                              <Col xs={24} md={12}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <EnvironmentOutlined style={{ color: '#52c41a' }} />
                                  <Text type="secondary">
                                    <strong>Đón:</strong> {detail?.diemdon?.tendiadiem || 'Như người đặt'}
                                  </Text>
                                </div>
                              </Col>
                              <Col xs={24} md={12}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                                  <Text type="secondary">
                                    <strong>Trả:</strong> {detail?.diemtra?.tendiadiem || 'Như người đặt'}
                                  </Text>
                                </div>
                              </Col>
                            </Row>
                          )}
                          
                          {detail?.ghichu && (
                            <div style={{ marginTop: '8px', padding: '6px 8px', backgroundColor: '#fff', borderRadius: '4px' }}>
                              <Text type="secondary" style={{ fontSize: '13px' }}>
                                💬 <strong>Ghi chú:</strong> {detail.ghichu}
                              </Text>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>
    );
  };

  // Render passenger details for a shift - new simplified version
  const renderPassengerDetailsNew = (chitietca: ChiTietCa) => {
    const shiftBookings = bookings[chitietca.machitietca] || [];
    
    if (shiftBookings.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '24px' }}>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            Chưa có hành khách đặt vé cho ca này
          </Text>
        </div>
      );
    }

    // Collect all passengers from all bookings
    const allPassengers: Array<{
      bookingId: number;
      name: string;
      phone: string;
      seats: number;
      pickup: string;
      dropoff: string;
      note?: string;
      trangthai?: string;
      isMainBooker: boolean;
    }> = [];

    shiftBookings.forEach(booking => {
      // Add main booker
      allPassengers.push({
        bookingId: booking.madatxe,
        name: booking?.manguoidung?.hoten || 'N/A',
        phone: booking?.manguoidung?.sodienthoai || 'N/A',
        seats: booking.soghe,
        pickup: booking?.diemdon?.tendiadiem || 'Chưa có thông tin',
        dropoff: booking?.diemtra?.tendiadiem || 'Chưa có thông tin',
        note: booking?.ghichu,
        trangthai: booking?.trangthai,
        isMainBooker: true
      });

      // Add additional passengers
      if (booking.chitietdatxe) {
        booking.chitietdatxe.forEach(detail => {
          allPassengers.push({
            bookingId: booking.madatxe,
            name: detail?.tenkhach || 'N/A',
            phone: detail?.sodienthoaikhach || 'N/A',
            seats: detail.soghe,
            pickup: detail?.diemdon?.tendiadiem || booking?.diemdon?.tendiadiem || 'Chưa có thông tin',
            dropoff: detail?.diemtra?.tendiadiem || booking?.diemtra?.tendiadiem || 'Chưa có thông tin',
            note: detail?.ghichu,
            trangthai: booking?.trangthai, // Use booking status for all passengers
            isMainBooker: false
          });
        });
      }
    });

    const totalPassengers = allPassengers.length;
    const totalSeats = allPassengers.reduce((sum, passenger) => sum + passenger.seats, 0);
    const totalBookings = shiftBookings.length;

    return (
      <div style={{ backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px' }}>
        {/* Summary */}
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#fff', borderRadius: '6px', border: '1px solid #e8e8e8' }}>
          <Title level={5} style={{ margin: 0, marginBottom: '8px', color: '#1890ff' }}>
            📊 Tổng quan hành khách
          </Title>
          <Space size="large">
            <Tag color="green" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalBookings} đặt vé
            </Tag>
            <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalPassengers} hành khách
            </Tag>
            <Tag color="orange" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalSeats} ghế
            </Tag>
          </Space>
        </div>

        {/* Passengers List */}
        <div style={{ display: 'grid', gap: '8px' }}>
          {allPassengers.map((passenger, index) => (
            <Card 
              key={`${passenger.bookingId}-${index}`}
              size="small" 
              style={{ 
                marginBottom: '0',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e8e8e8'
              }}
              title={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#1890ff', fontWeight: 'bold' }}>
                    👤 {passenger.name} (Đặt vé #{passenger.bookingId})
                  </span>
                  <Tag color="purple" style={{ fontSize: '12px' }}>
                    {passenger.seats} ghế
                  </Tag>
                </div>
              }
            >
              <Row gutter={[16, 8]}>
                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <PhoneOutlined style={{ color: '#1890ff' }} />
                    <Text>{passenger.phone}</Text>
                  </div>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <EnvironmentOutlined style={{ color: '#52c41a' }} />
                    <Text type="secondary">
                      <strong>Đón:</strong> {passenger.pickup}
                    </Text>
                  </div>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                    <Text type="secondary">
                      <strong>Trả:</strong> {passenger.dropoff}
                    </Text>
                  </div>
                </Col>
              </Row>

              {passenger.note && (
                <div style={{ marginTop: '8px', padding: '6px 8px', backgroundColor: '#f6ffed', borderRadius: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '13px' }}>
                    💬 <strong>Ghi chú:</strong> {passenger.note}
                  </Text>
                </div>
              )}

              {/* Status and Action Buttons - only for main booker */}
              {passenger.isMainBooker && (
                <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#fff', borderRadius: '4px', border: '1px solid #e8e8e8' }}>
                  <Row gutter={[8, 8]} align="middle">
                    <Col>
                      <Text strong style={{ fontSize: '13px', color: '#666' }}>
                        Trạng thái:
                      </Text>
                    </Col>
                    <Col>
                      <Tag color={
                        passenger.trangthai === 'Đã đón' ? 'orange' :
                        passenger.trangthai === 'Đã trả' ? 'green' :
                        passenger.trangthai === 'Đã đặt' ? 'blue' : 'default'
                      }>
                        {passenger.trangthai || 'Chưa xác định'}
                      </Tag>
                    </Col>
                    <Col flex="auto" />
                    <Col>
                      <Space size="small">
                        <Button
                          size="small"
                          type="primary"
                          disabled={passenger.trangthai === 'Đã đón' || passenger.trangthai === 'Đã trả'}
                          onClick={() => updateBookingStatus(passenger.bookingId, 'Đã đón', chitietca.machitietca)}
                        >
                          Đã đón
                        </Button>
                        <Button
                          size="small"
                          type="primary"
                          style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                          disabled={passenger.trangthai !== 'Đã đón'}
                          onClick={() => updateBookingStatus(passenger.bookingId, 'Đã trả', chitietca.machitietca)}
                        >
                          Đã trả
                        </Button>
                      </Space>
                    </Col>
                  </Row>
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>
          <CarOutlined /> Ca làm việc của tài xế
        </Title>
        
        {/* Date Selection */}
        <div style={{ marginBottom: '24px' }}>
          <Space>
            <CalendarOutlined />
            <Text strong>Chọn ngày:</Text>
            <DatePicker            placeholder="Chọn ngày"
            format="DD/MM/YYYY"
            onChange={handleDateChange}
            disabledDate={(current) => current && current < dayjs().startOf('day')}
            disabled={!currentUser}
          />
          </Space>
        </div>        {selectedDate && currentUser && (
          <>
            <Divider />
            <Alert
              message={`Ca làm việc của tài xế ${currentUser.hoten} ngày ${selectedDate.format('DD/MM/YYYY')}`}
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
          </>
        )}

        {/* Shifts Table */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <div style={{ marginTop: '16px' }}>
              <Text>Đang tải danh sách ca làm việc...</Text>
            </div>
          </div>
        ) : shiftDetails.length > 0 ? (
          <div>
            <Table
              dataSource={shiftDetails}
              columns={shiftDetailColumns}
              rowKey="machitietca"
              pagination={false}              expandable={{
                expandedRowRender: (record) => {
                  if (!loadedBookings.has(record.machitietca)) {
                    loadBookings(record);
                    return (
                      <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Spin />
                        <div style={{ marginTop: '8px' }}>
                          <Text>Đang tải danh sách hành khách...</Text>
                        </div>
                      </div>
                    );
                  }
                  return renderPassengerDetailsNew(record);
                },
                rowExpandable: () => true,
              }}
            />
          </div>        ) : selectedDate && currentUser ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Text type="secondary">Bạn không có ca làm việc nào trong ngày đã chọn</Text>
          </div>
        ) : !currentUser ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin />
            <div style={{ marginTop: '8px' }}>
              <Text>Đang tải thông tin tài xế...</Text>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Text type="secondary">Vui lòng chọn ngày để xem ca làm việc của bạn</Text>
          </div>
        )}
      </Card>
    </div>
  );
};

export default DriverShifts;
