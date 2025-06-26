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
  trangthai?: string;  chitietdatxe?: {
    machitiet?: number; // ID của chi tiết đặt xe (Chitietdatxe)
    chitiet_id?: number;
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
    trangthai?: string;
    machitietca?: number | {
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

const DriverShifts: React.FC = () => {  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [shiftDetails, setShiftDetails] = useState<ChiTietCa[]>([]);
  const [bookings, setBookings] = useState<Record<number, Booking[]>>({});  const [loading, setLoading] = useState(false);
  // State for passenger prices and loading status
  const [passengerPrices, setPassengerPrices] = useState<{[key: string]: {totalPrice: number; distance: number; loading: boolean; error?: string}}>({});
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
      setLoading(true);      const dateString = date.format('YYYY-MM-DD');
      const requestData = { "ngay": dateString };
      
      console.log(`📅 [LOAD SHIFTS] Loading shifts for date: ${dateString}`);
      const response = await api.getShiftsByCa(requestData);
      console.log(`📨 [LOAD SHIFTS] Raw shifts response:`, response);
      
      let shiftsData = [];
      if (Array.isArray(response)) {
        shiftsData = response;
      } else if (response && Array.isArray(response.data)) {
        shiftsData = response.data;
      } else if (response && Array.isArray(response.results)) {
        shiftsData = response.results;      } else if (response && response.ca) {
        shiftsData = Array.isArray(response.ca) ? response.ca : [response.ca];
      }
      
      console.log(`📋 [LOAD SHIFTS] Extracted shifts:`, {
        shiftsCount: shiftsData.length,
        shifts: shiftsData.map((s: any) => ({ maca: s.maca, gioxuatphat: s.gioxuatphat }))
      });
      
      setShifts(shiftsData);
        // Load shift details for each shift
      const allShiftDetails: ChiTietCa[] = [];
      for (const shift of shiftsData) {
        try {          console.log(`🔍 [SHIFT DETAILS] Loading details for shift ${shift.maca}...`);
          const details = await api.getShiftDetails(shift.maca);
          console.log(`📨 [SHIFT DETAILS] Raw details for shift ${shift.maca}:`, details);
          
          let detailsArray = [];
          if (Array.isArray(details)) {
            detailsArray = details;
          } else if (details && Array.isArray(details.data)) {
            detailsArray = details.data;
          }
          
          console.log(`📋 [SHIFT DETAILS] Extracted details for shift ${shift.maca}:`, {
            detailsCount: detailsArray.length,
            details: detailsArray.map((d: any) => ({ 
              machitietca: d.machitietca, 
              mataixe: d.taixe_info?.mataixe 
            }))
          });
            // Filter only shift details for current driver
          if (currentUser && currentUser.manguoidung) {            console.log(`👤 [FILTER DRIVER] Filtering for current user: ${currentUser.manguoidung}`);
            const driverShiftDetails = detailsArray.filter((detail: ChiTietCa) => {
              const match = detail.taixe_info?.mataixe === currentUser.manguoidung;
              console.log(`🔍 [FILTER DRIVER] Detail ${detail.machitietca} - mataixe: ${detail.taixe_info?.mataixe}, matches: ${match}`);
              return match;
            });
              console.log(`✅ [FILTER DRIVER] Driver shift details for shift ${shift.maca}:`, {
              filteredCount: driverShiftDetails.length,
              filteredDetails: driverShiftDetails.map((d: ChiTietCa) => d.machitietca)
            });
            
            allShiftDetails.push(...driverShiftDetails);
          }
        } catch (error) {
          console.error(`❌ Error loading details for shift ${shift.maca}:`, error);        }
      }
        console.log(`✅ [LOAD SHIFTS] Final all shift details:`, {
        totalShiftDetails: allShiftDetails.length,
        shiftDetailIds: allShiftDetails.map((d: ChiTietCa) => d.machitietca)
      });
      
      setShiftDetails(allShiftDetails);
      
    } catch (error: any) {
      console.error('❌ Error loading shifts:', error);
      message.error('Không thể tải danh sách ca làm việc');
      setShifts([]);
      setShiftDetails([]);
    } finally {
      setLoading(false);
    }
  };// Load bookings for a specific shift detail
  const loadBookings = async (chitietca: ChiTietCa) => {
    console.log(`🔍 [LOAD BOOKINGS] Starting to load bookings for shift detail:`, {
      machitietca: chitietca.machitietca,
      maca: chitietca.maca,
      isLoading: bookingLoading[chitietca.machitietca],
      alreadyLoaded: loadedBookings.has(chitietca.machitietca)
    });

    // Check if already loading or loaded
    if (bookingLoading[chitietca.machitietca] || loadedBookings.has(chitietca.machitietca)) {
      console.log(`⏭️ [LOAD BOOKINGS] Skipping - already loading or loaded`);
      return;
    }
    
    try {      setBookingLoading(prev => ({ ...prev, [chitietca.machitietca]: true }));
      setLoadedBookings(prev => new Set(prev).add(chitietca.machitietca));
      
      console.log(`📞 [LOAD BOOKINGS] Calling api.getBookings()...`);
      const response = await api.getBookings();
      console.log(`📨 [LOAD BOOKINGS] Raw API response:`, response);
      
      // Filter bookings by maca and machitietca
      let allBookings = [];
      if (Array.isArray(response)) {
        allBookings = response;
      } else if (response && Array.isArray(response.data)) {
        allBookings = response.data;      } else if (response && Array.isArray(response.results)) {
        allBookings = response.results;
      }
      
      console.log(`📋 [LOAD BOOKINGS] All bookings extracted:`, {
        totalBookings: allBookings.length,
        bookingIds: allBookings.map((b: any) => b.madatxe),
        firstBooking: allBookings[0] || null
      });      const filteredBookings = allBookings.filter((booking: Booking) => {
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

        // Check if main booking matches
        const mainBookingMatchesCa = bookingMaca === chitietca.maca;
        const mainBookingMatchesChitietCa = bookingMachitietca === chitietca.machitietca;
        const mainBookingMatches = mainBookingMatchesCa && mainBookingMatchesChitietCa;
        
        // Check if any detail in chitietdatxe matches
        let hasMatchingDetail = false;
        if (booking.chitietdatxe && Array.isArray(booking.chitietdatxe)) {
          hasMatchingDetail = booking.chitietdatxe.some((detail: any) => {
            let detailMaca = null;
            let detailMachitietca = null;
            
            // Extract maca from detail
            if (detail.machitietca) {
              if (typeof detail.machitietca === 'object' && detail.machitietca.maca) {
                detailMaca = typeof detail.machitietca.maca === 'object' ? detail.machitietca.maca.maca : detail.machitietca.maca;
                detailMachitietca = detail.machitietca.machitietca;
              }
            }
            
            const detailMatchesCa = detailMaca === chitietca.maca;
            const detailMatchesChitietCa = detailMachitietca === chitietca.machitietca;
            
            return detailMatchesCa && detailMatchesChitietCa;
          });
        }
        
        const isMatch = mainBookingMatches || hasMatchingDetail;
        
        // Enhanced logging for debugging
        if (booking.madatxe) { // Log all bookings briefly
          console.log(`🔍 [FILTER] Booking ${booking.madatxe}:`, {
            bookingMaca,
            bookingMachitietca,
            targetMaca: chitietca.maca,
            targetMachitietca: chitietca.machitietca,
            mainBookingMatches,
            hasMatchingDetail,
            isMatch,
            rawMaca: booking.maca,
            rawMachitietca: booking.machitietca,
            chitietdatxeCount: booking.chitietdatxe?.length || 0
          });
        }
          
        return isMatch;
      });
      
      console.log(`✅ [LOAD BOOKINGS] Filtered bookings for shift detail ${chitietca.machitietca}:`, {
        totalFiltered: filteredBookings.length,
        filteredBookingIds: filteredBookings.map((b: any) => b.madatxe),
        filteredBookings: filteredBookings
      });
      
      setBookings(prev => ({
        ...prev,
        [chitietca.machitietca]: filteredBookings
      }));
      
    } catch (error: any) {
      console.error('❌ [LOAD BOOKINGS] Error loading bookings:', error);
      message.error('Không thể tải danh sách hành khách');    } finally {
      setBookingLoading(prev => ({ ...prev, [chitietca.machitietca]: false }));
    }
  };

  // Update booking status (for main booker or booking detail)
  const updatePassengerStatus = async (
    bookingId: number, 
    chitietId: number | undefined, 
    trangthai: string, 
    chitietcaId: number
  ) => {
    try {
      console.log(`� START - Updating passenger status:`, {
        bookingId,
        chitietId,
        trangthai,
        type: chitietId ? 'Additional Passenger (Detail API)' : 'Main Booker (Booking API)'
      });
      
      if (chitietId) {
        // Cập nhật trạng thái chi tiết đặt xe (hành khách bổ sung) với machitiet
        console.log(`� Calling updateBookingDetailStatus API with machitiet=${chitietId}, trangthai="${trangthai}"`);
        const response = await api.updateBookingDetailStatus(chitietId, { trangthai });
        console.log(`✅ API Response:`, response);
        message.success(`Đã cập nhật trạng thái hành khách bổ sung thành: ${trangthai}`);
      } else {
        // Cập nhật trạng thái booking chính (người đặt chính)
        console.log(`� Calling updateBookingStatus API with bookingId=${bookingId}, trangthai="${trangthai}"`);
        const response = await api.updateBookingStatus(bookingId, { trangthai });
        console.log(`✅ API Response:`, response);
        message.success(`Đã cập nhật trạng thái người đặt chính thành: ${trangthai}`);
      }
      
      console.log(`🔄 Reloading bookings for shift detail ${chitietcaId}...`);
      
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
        console.log(`✅ Successfully reloaded bookings for shift detail ${chitietcaId}`);
      }
      
    } catch (error: any) {
      console.error('❌ Error updating passenger status:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url
      });
      message.error('Không thể cập nhật trạng thái hành khách');
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
                      </div>                      {booking?.diemdon?.vido != null && booking?.diemdon?.kinhdo != null && (
                        <div style={{ fontSize: '11px', color: '#8c8c8c', marginLeft: '20px', marginTop: '2px' }}>
                          📍 {Number(booking.diemdon.vido).toFixed(6)}, {Number(booking.diemdon.kinhdo).toFixed(6)}
                        </div>
                      )}
                      {/* Debug: Show coordinates availability */}
                      {(booking?.diemdon?.vido == null || booking?.diemdon?.kinhdo == null) && (
                        <div style={{ fontSize: '10px', color: '#ff4d4f', marginLeft: '20px', marginTop: '2px' }}>
                          ⚠️ Tọa độ: vido={booking?.diemdon?.vido || 'null'}, kinhdo={booking?.diemdon?.kinhdo || 'null'}
                        </div>
                      )}
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                        <Text type="secondary">
                          <strong>Trả:</strong> {booking?.diemtra?.tendiadiem || 'Chưa có thông tin'}
                        </Text>
                      </div>                      {booking?.diemtra?.vido != null && booking?.diemtra?.kinhdo != null && (
                        <div style={{ fontSize: '11px', color: '#8c8c8c', marginLeft: '20px', marginTop: '2px' }}>
                          📍 {Number(booking.diemtra.vido).toFixed(6)}, {Number(booking.diemtra.kinhdo).toFixed(6)}
                        </div>
                      )}
                      {/* Debug: Show coordinates availability */}
                      {(booking?.diemtra?.vido == null || booking?.diemtra?.kinhdo == null) && (
                        <div style={{ fontSize: '10px', color: '#ff4d4f', marginLeft: '20px', marginTop: '2px' }}>
                          ⚠️ Tọa độ: vido={booking?.diemtra?.vido || 'null'}, kinhdo={booking?.diemtra?.kinhdo || 'null'}
                        </div>
                      )}
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
                            onClick={() => updatePassengerStatus(booking.madatxe, undefined, 'Đã đón', chitietca.machitietca)}
                          >
                            Đã đón
                          </Button>
                          <Button
                            size="small"
                            type="primary"
                            style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                            disabled={booking?.trangthai !== 'Đã đón'}
                            onClick={() => updatePassengerStatus(booking.madatxe, undefined, 'Đã trả', chitietca.machitietca)}
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
                                </div>                                {detail?.diemdon?.vido != null && detail?.diemdon?.kinhdo != null && (
                                  <div style={{ fontSize: '11px', color: '#8c8c8c', marginLeft: '20px', marginTop: '2px' }}>
                                    📍 {Number(detail.diemdon.vido).toFixed(6)}, {Number(detail.diemdon.kinhdo).toFixed(6)}
                                  </div>
                                )}
                                {/* Debug: Show coordinates availability */}
                                {(detail?.diemdon?.vido == null || detail?.diemdon?.kinhdo == null) && (
                                  <div style={{ fontSize: '10px', color: '#ff4d4f', marginLeft: '20px', marginTop: '2px' }}>
                                    ⚠️ Tọa độ đón: vido={detail?.diemdon?.vido || 'null'}, kinhdo={detail?.diemdon?.kinhdo || 'null'}
                                  </div>
                                )}
                              </Col>
                              <Col xs={24} md={12}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                                  <Text type="secondary">
                                    <strong>Trả:</strong> {detail?.diemtra?.tendiadiem || 'Như người đặt'}
                                  </Text>
                                </div>                                {detail?.diemtra?.vido != null && detail?.diemtra?.kinhdo != null && (
                                  <div style={{ fontSize: '11px', color: '#8c8c8c', marginLeft: '20px', marginTop: '2px' }}>
                                    📍 {Number(detail.diemtra.vido).toFixed(6)}, {Number(detail.diemtra.kinhdo).toFixed(6)}
                                  </div>
                                )}
                                {/* Debug: Show coordinates availability */}
                                {(detail?.diemtra?.vido == null || detail?.diemtra?.kinhdo == null) && (
                                  <div style={{ fontSize: '10px', color: '#ff4d4f', marginLeft: '20px', marginTop: '2px' }}>
                                    ⚠️ Tọa độ trả: vido={detail?.diemtra?.vido || 'null'}, kinhdo={detail?.diemtra?.kinhdo || 'null'}
                                  </div>
                                )}
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
  };  // Render passenger details for a shift - new simplified version
  const renderPassengerDetailsNew = (chitietca: ChiTietCa) => {    const shiftBookings = bookings[chitietca.machitietca] || [];
    
    console.log(`🎨 [RENDER] Rendering passenger details for shift detail ${chitietca.machitietca}:`, {
      shiftBookingsCount: shiftBookings.length,
      allBookingsState: Object.keys(bookings).map(key => ({ 
        key, 
        count: bookings[parseInt(key)]?.length || 0 
      })),
      shiftBookings: shiftBookings
    });
    
    if (shiftBookings.length === 0) {
      console.log(`⚠️ [RENDER] No bookings found for shift detail ${chitietca.machitietca}`);
      return (
        <div style={{ textAlign: 'center', padding: '24px' }}>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            Chưa có hành khách đặt vé cho ca này
          </Text>
        </div>
      );
    }// Collect all passengers from all bookings
    const allPassengers: Array<{
      bookingId: number;
      chitietId?: number; // ID của chi tiết đặt vé (machitiet cho khách phụ)
      name: string;
      phone: string;
      seats: number;
      pickup: string;
      dropoff: string;
      pickupCoords?: { vido: number; kinhdo: number };
      dropoffCoords?: { vido: number; kinhdo: number };
      note?: string;
      trangthai?: string;
      isMainBooker: boolean;
      totalPrice?: number; // Tổng tiền phải trả
      distance?: number; // Khoảng cách (km)
    }> = [];    shiftBookings.forEach(booking => {
      // Add main booker only if booking's main machitietca matches
      let bookingMachitietca = null;
      if (booking.machitietca) {
        bookingMachitietca = typeof booking.machitietca === 'object' ? booking.machitietca.machitietca : booking.machitietca;
      }
      
      const mainBookingMatches = bookingMachitietca === chitietca.machitietca;
      
      if (mainBookingMatches) {
        const mainBooker = {
          bookingId: booking.madatxe,
          name: booking?.manguoidung?.hoten || 'N/A',
          phone: booking?.manguoidung?.sodienthoai || 'N/A',
          seats: booking.soghe,
          pickup: booking?.diemdon?.tendiadiem || 'Chưa có thông tin',
          dropoff: booking?.diemtra?.tendiadiem || 'Chưa có thông tin',
          note: booking?.ghichu,
          trangthai: booking?.trangthai,
          isMainBooker: true,
          pickupCoords: booking?.diemdon?.vido != null && booking?.diemdon?.kinhdo != null ? {
            vido: booking.diemdon.vido,
            kinhdo: booking.diemdon.kinhdo
          } : undefined,
          dropoffCoords: booking?.diemtra?.vido != null && booking?.diemtra?.kinhdo != null ? {
            vido: booking.diemtra.vido,
            kinhdo: booking.diemtra.kinhdo
          } : undefined,
          totalPrice: 0,
          distance: 0
        };
        allPassengers.push(mainBooker);
      }

      // Add additional passengers from chitietdatxe that match this shift detail
      if (booking.chitietdatxe) {
        booking.chitietdatxe.forEach((detail, detailIndex) => {
          let detailMachitietca = null;
          
          // Extract machitietca from detail
          if (detail.machitietca) {
            detailMachitietca = typeof detail.machitietca === 'object' ? detail.machitietca.machitietca : detail.machitietca;
          }
          
          // Only add this detail if it matches the current shift detail
          if (detailMachitietca === chitietca.machitietca) {
            const additionalPassenger = {
              bookingId: booking.madatxe,
              chitietId: detail.machitiet, // Dùng machitiet để cập nhật trạng thái chi tiết
              name: detail?.tenkhach || 'N/A',
              phone: detail?.sodienthoaikhach || 'N/A',
              seats: detail.soghe,
              pickup: detail?.diemdon?.tendiadiem || booking?.diemdon?.tendiadiem || 'Chưa có thông tin',
              dropoff: detail?.diemtra?.tendiadiem || booking?.diemtra?.tendiadiem || 'Chưa có thông tin',
              note: detail?.ghichu,
              trangthai: detail?.trangthai || booking?.trangthai, // Ưu tiên trạng thái riêng của chi tiết
              isMainBooker: false,
              pickupCoords: detail?.diemdon?.vido != null && detail?.diemdon?.kinhdo != null ? {
                vido: detail.diemdon.vido,
                kinhdo: detail.diemdon.kinhdo
              } : (booking?.diemdon?.vido != null && booking?.diemdon?.kinhdo != null ? {
                vido: booking.diemdon.vido,
                kinhdo: booking.diemdon.kinhdo
              } : undefined),
              dropoffCoords: detail?.diemtra?.vido != null && detail?.diemtra?.kinhdo != null ? {
                vido: detail.diemtra.vido,
                kinhdo: detail.diemtra.kinhdo
              } : (booking?.diemtra?.vido != null && booking?.diemtra?.kinhdo != null ? {
                vido: booking.diemtra.vido,
                kinhdo: booking.diemtra.kinhdo
              } : undefined),
              totalPrice: 0,
              distance: 0
            };
            allPassengers.push(additionalPassenger);
          }
        });
      }
    });console.log('� All passengers ready:', allPassengers.map((p, index) => ({
      index,
      name: p.name,
      isMainBooker: p.isMainBooker,
      chitietId: p.chitietId,
      canUpdate: p.isMainBooker ? 'booking API' : (p.chitietId ? 'detail API' : 'NO API - missing ID')
    })));    const totalPassengers = allPassengers.length;
    const totalSeats = allPassengers.reduce((sum, passenger) => sum + passenger.seats, 0);
    const totalBookings = shiftBookings.length;
    
    // Calculate total revenue from actual price data
    const totalRevenue = allPassengers.reduce((sum, passenger) => {
      const passengerKey = `${passenger.bookingId}-${passenger.isMainBooker ? 'main' : passenger.chitietId || 'additional'}`;
      const priceData = passengerPrices[passengerKey];
      return sum + (priceData?.totalPrice || 0);
    }, 0);

    return (
      <div style={{ backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px' }}>
        {/* Summary */}
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#fff', borderRadius: '6px', border: '1px solid #e8e8e8' }}>
          <Title level={5} style={{ margin: 0, marginBottom: '8px', color: '#1890ff' }}>
            📊 Tổng quan hành khách
          </Title>          <Space size="large">
            <Tag color="green" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalBookings} đặt vé
            </Tag>
            <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalPassengers} hành khách
            </Tag>
            <Tag color="orange" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {totalSeats} ghế
            </Tag>
            <Tag color="red" style={{ fontSize: '14px', padding: '4px 12px' }}>
              💰 {totalRevenue.toLocaleString('vi-VN')} VNĐ
            </Tag>
          </Space><div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#f6ffed', borderRadius: '4px', fontSize: '13px' }}>
            <Text type="secondary">
              💡 <strong>Lưu ý:</strong> Mỗi hành khách có thể được cập nhật trạng thái riêng biệt. 
              Người đặt chính và hành khách bổ sung có thể có trạng thái khác nhau (Đã đặt, Đã đón, Đã trả).
            </Text>
          </div>
        </div>        {/* Passengers List */}
        <div style={{ display: 'grid', gap: '8px' }}>
          {allPassengers.map((passenger, index) => (
            <Card 
              key={`${passenger.bookingId}-${index}`}
              size="small" 
              style={{ 
                marginBottom: '0',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e8e8e8'
              }}              title={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#1890ff', fontWeight: 'bold' }}>
                    {passenger.isMainBooker ? '👤 ' : '👥 '}{passenger.name} 
                    {passenger.isMainBooker ? ' (Người đặt chính)' : ' (Hành khách bổ sung)'}
                    <Text type="secondary" style={{ fontSize: '12px', marginLeft: '8px' }}>
                      Đặt vé #{passenger.bookingId}
                    </Text>
                  </span>                  <span>
                    <Tag color="purple" style={{ fontSize: '12px' }}>
                      {passenger.seats} ghế
                    </Tag>
                    {(() => {
                      const passengerKey = `${passenger.bookingId}-${passenger.isMainBooker ? 'main' : passenger.chitietId || 'additional'}`;
                      const priceData = passengerPrices[passengerKey];
                      
                      if (priceData?.loading) {
                        return (
                          <Tag color="red" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            💰 Đang tính...
                          </Tag>
                        );
                      } else if (priceData?.error) {
                        return (
                          <Tag color="red" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            💰 Lỗi
                          </Tag>
                        );
                      } else if (priceData?.totalPrice) {
                        return (
                          <Tag color="red" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            💰 {priceData.totalPrice.toLocaleString('vi-VN')} VNĐ
                          </Tag>
                        );
                      } else {
                        // Calculate price on first render
                        if (passenger.pickupCoords && passenger.dropoffCoords) {
                          setTimeout(() => {
                            calculatePassengerPrice({
                              pickupCoords: passenger.pickupCoords,
                              dropoffCoords: passenger.dropoffCoords,
                              seats: passenger.seats,
                              passengerKey
                            });
                          }, 100 * index); // Stagger API calls
                        }
                        return (
                          <Tag color="red" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            💰 Chưa tính
                          </Tag>
                        );
                      }
                    })()}
                    {(() => {
                      const passengerKey = `${passenger.bookingId}-${passenger.isMainBooker ? 'main' : passenger.chitietId || 'additional'}`;
                      const priceData = passengerPrices[passengerKey];
                      
                      if (priceData?.loading) {
                        return (
                          <Tag color="cyan" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            📏 Đang tính...
                          </Tag>
                        );
                      } else if (priceData?.distance) {
                        return (
                          <Tag color="cyan" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            📏 {priceData.distance.toFixed(1)} km
                          </Tag>
                        );
                      } else {
                        return (
                          <Tag color="cyan" style={{ fontSize: '12px', marginLeft: '4px' }}>
                            📏 Chưa tính
                          </Tag>
                        );
                      }
                    })()}
                  </span>
                </div>
              }
            >
              <Row gutter={[16, 8]}>
                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <PhoneOutlined style={{ color: '#1890ff' }} />
                    <Text>{passenger.phone}</Text>
                  </div>
                </Col>                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <EnvironmentOutlined style={{ color: '#52c41a' }} />
                    <Text type="secondary">
                      <strong>Đón:</strong> {passenger.pickup}
                    </Text>
                  </div>
                  {/* Hiển thị tọa độ điểm đón */}
                  {passenger.pickupCoords && passenger.pickupCoords.vido != null && passenger.pickupCoords.kinhdo != null && (
                    <div style={{ marginLeft: '22px', marginTop: '2px' }}>
                      <Text style={{ fontSize: '11px', color: '#999' }}>
                        📍 ({Number(passenger.pickupCoords.vido).toFixed(6)}, {Number(passenger.pickupCoords.kinhdo).toFixed(6)})
                      </Text>
                    </div>
                  )}
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                    <Text type="secondary">
                      <strong>Trả:</strong> {passenger.dropoff}
                    </Text>
                  </div>
                  {/* Hiển thị tọa độ điểm trả */}
                  {passenger.dropoffCoords && passenger.dropoffCoords.vido != null && passenger.dropoffCoords.kinhdo != null && (
                    <div style={{ marginLeft: '22px', marginTop: '2px' }}>
                      <Text style={{ fontSize: '11px', color: '#999' }}>
                        📍 ({Number(passenger.dropoffCoords.vido).toFixed(6)}, {Number(passenger.dropoffCoords.kinhdo).toFixed(6)})
                      </Text>
                    </div>
                  )}
                </Col>
              </Row>

              {passenger.note && (
                <div style={{ marginTop: '8px', padding: '6px 8px', backgroundColor: '#f6ffed', borderRadius: '4px' }}>
                  <Text type="secondary" style={{ fontSize: '13px' }}>
                    💬 <strong>Ghi chú:</strong> {passenger.note}
                  </Text>
                </div>
              )}              {/* Status and Action Buttons - for all passengers */}
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
                    <Space size="small">                      <Button
                        size="small"
                        type="primary"
                        disabled={passenger.trangthai === 'Đã đón' || passenger.trangthai === 'Đã trả'}                        onClick={() => {
                          console.log(`🔍 BUTTON CLICK - Button clicked for passenger:`, {
                            name: passenger.name,
                            isMainBooker: passenger.isMainBooker,
                            bookingId: passenger.bookingId,
                            chitietId: passenger.chitietId,
                            willCallAPI: passenger.isMainBooker ? 'updateBookingStatus' : 'updateBookingDetailStatus',
                            apiParam: passenger.isMainBooker ? passenger.bookingId : passenger.chitietId
                          });
                          updatePassengerStatus(passenger.bookingId, passenger.chitietId, 'Đã đón', chitietca.machitietca);
                        }}
                      >
                        Đã đón
                      </Button>
                      <Button
                        size="small"
                        type="primary"
                        style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                        disabled={passenger.trangthai !== 'Đã đón'}                        onClick={() => {
                          console.log(`🔍 BUTTON CLICK - Button clicked for passenger:`, {
                            name: passenger.name,
                            isMainBooker: passenger.isMainBooker,
                            bookingId: passenger.bookingId,
                            chitietId: passenger.chitietId,
                            willCallAPI: passenger.isMainBooker ? 'updateBookingStatus' : 'updateBookingDetailStatus',
                            apiParam: passenger.isMainBooker ? passenger.bookingId : passenger.chitietId
                          });
                          updatePassengerStatus(passenger.bookingId, passenger.chitietId, 'Đã trả', chitietca.machitietca);
                        }}
                      >
                        Đã trả
                      </Button>
                    </Space>
                  </Col>
                </Row>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  };
  // Calculate price for passenger
  const calculatePassengerPrice = async (passenger: {
    pickupCoords?: { vido: number; kinhdo: number };
    dropoffCoords?: { vido: number; kinhdo: number };
    seats: number;
    passengerKey: string; // Unique key for caching
  }) => {
    try {
      if (!passenger.pickupCoords || !passenger.dropoffCoords) {
        return { totalPrice: 0, distance: 0 };
      }

      // Set loading state
      setPassengerPrices(prev => ({
        ...prev,
        [passenger.passengerKey]: { ...prev[passenger.passengerKey], loading: true, error: undefined }
      }));

      // Call calculatePrice API similar to Booking/StaffBooking
      const priceResponse = await api.calculatePrice({
        lat_don: passenger.pickupCoords.vido.toString(),
        lon_don: passenger.pickupCoords.kinhdo.toString(),
        lat_tra: passenger.dropoffCoords.vido.toString(),
        lon_tra: passenger.dropoffCoords.kinhdo.toString()
      });

      if (priceResponse.success && (priceResponse.giatien || priceResponse.giacuoc)) {
        const unitPrice = priceResponse.giatien || priceResponse.giacuoc || 0;
        const totalPrice = unitPrice * passenger.seats;
        const distance = priceResponse.khoangcach || 0;

        const result = { totalPrice, distance, loading: false };
        
        // Update state
        setPassengerPrices(prev => ({
          ...prev,
          [passenger.passengerKey]: result
        }));

        return result;
      } else {
        const result = { totalPrice: 0, distance: 0, loading: false, error: 'Không thể tính giá' };
        setPassengerPrices(prev => ({
          ...prev,
          [passenger.passengerKey]: result
        }));
        return result;
      }
    } catch (error) {
      console.error('Error calculating price for passenger:', error);
      const result = { totalPrice: 0, distance: 0, loading: false, error: 'Lỗi khi tính giá' };
      setPassengerPrices(prev => ({
        ...prev,
        [passenger.passengerKey]: result
      }));
      return result;
    }
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
