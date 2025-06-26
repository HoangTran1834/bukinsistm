import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Form,
  DatePicker,
  Select,
  AutoComplete,
  Button,
  Space,
  message,
  Row,
  Col,
  Typography,
  Divider,
  Spin,
  Alert,
  Input,
  InputNumber,
  Modal,
  Steps
} from 'antd';
import {
  CalendarOutlined,
  EnvironmentOutlined,
  CarOutlined,
  ClockCircleOutlined,
  InfoCircleOutlined,
  UserOutlined,
  PhoneOutlined,
  DollarOutlined,
  PlusOutlined,
  DeleteOutlined,
  SearchOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../api/backend';

const { Title, Text } = Typography;
const { Option } = Select;
const { Step } = Steps;

interface UserResponse {
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

interface Shift {
  maca: number;
  mahuyenxuatphat: {
    mahuyen: number;
    tenhuyen: string;
  };
  gioxuatphat: string;
  ngayxuatphat: string;
}

interface AddressResult {
  place_id: number;
  lat: string;
  lon: string;
  display_name: string;
  name?: string;
}

interface LocationData {
  madiadiem: number;
  tendiadiem: string;
  vido: number;
  kinhdo: number;
}

interface PassengerDetail {
  tenkhach: string;
  sodienthoaikhach: string;
  soghe: number;
  ghichu?: string;
  selectedPickup: AddressResult | null;
  selectedDropoff: AddressResult | null;
  diemdon?: number;
  diemtra?: number;
  // Price information for this passenger
  priceInfo?: PriceInfo | null;
  priceLoading?: boolean;
}

interface PriceInfo {
  success?: boolean;
  giatien?: number;
  giacuoc?: number;
  tuyenduong?: {
    matuyenduong: number;
    huyendon: {
      mahuyen: number;
      tenhuyen: string;
    };
    huyentra: {
      mahuyen: number;
      tenhuyen: string;
    };
    giacuoc: string;
    huongchay: number;
  };
  huyen_don?: {
    mahuyen: number;
    tenhuyen: string;
  };
  huyen_tra?: {
    mahuyen: number;
    tenhuyen: string;
  };
  coordinates?: {
    pickup: {
      lat: string;
      lon: string;
    };
    dropoff: {
      lat: string;
      lon: string;
    };
  };
  khoangcach?: number;
  thoigian?: number;
  message?: string;
}

const StaffBooking: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  
  // Customer search/create states
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerSearchLoading, setCustomerSearchLoading] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<UserResponse | null>(null);
  const [showCreateCustomer, setShowCreateCustomer] = useState(false);
  const [createCustomerForm] = Form.useForm();
  const [createCustomerLoading, setCreateCustomerLoading] = useState(false);
  
  // Booking states (similar to original Booking.tsx)
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);
  const [selectedShift, setSelectedShift] = useState<number | null>(null);
  
  // Address search states
  const [pickupOptions, setPickupOptions] = useState<{ value: string; key: string; data: AddressResult }[]>([]);
  const [dropoffOptions, setDropoffOptions] = useState<{ value: string; key: string; data: AddressResult }[]>([]);
  const [pickupLoading, setPickupLoading] = useState(false);
  const [dropoffLoading, setDropoffLoading] = useState(false);
  
  // Passenger autocomplete options
  const [passengerPickupOptions, setPassengerPickupOptions] = useState<Record<number, { value: string; key: string; data: AddressResult }[]>>({});
  const [passengerDropoffOptions, setPassengerDropoffOptions] = useState<Record<number, { value: string; key: string; data: AddressResult }[]>>({});
  const [passengerPickupLoading, setPassengerPickupLoading] = useState<Record<number, boolean>>({});
  const [passengerDropoffLoading, setPassengerDropoffLoading] = useState<Record<number, boolean>>({});
  const [passengerSearchTimeouts, setPassengerSearchTimeouts] = useState<Record<string, number>>({});
  
  // Selected locations
  const [selectedPickup, setSelectedPickup] = useState<AddressResult | null>(null);
  const [selectedDropoff, setSelectedDropoff] = useState<AddressResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState<number | null>(null);
  
  // Price and passenger states
  const [priceInfo, setPriceInfo] = useState<PriceInfo | null>(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [passengers, setPassengers] = useState<PassengerDetail[]>([]);
  const [showPassengerModal, setShowPassengerModal] = useState(false);
  const [mainBookerSeats, setMainBookerSeats] = useState(1);
  const [totalSeats, setTotalSeats] = useState(1);

  // Generate random password for new customers
  const generatePassword = () => {
    return Math.random().toString(36).slice(-8) + Math.random().toString(36).slice(-8);
  };

  // Search customer by phone
  const searchCustomerByPhone = async () => {
    if (!customerPhone.trim()) {
      message.error('Vui lòng nhập số điện thoại');
      return;
    }

    try {
      setCustomerSearchLoading(true);
      console.log('🔍 Searching customer by phone:', customerPhone);
      
      const user = await api.getUserByPhone(customerPhone.trim());
      
      if (user) {
        console.log('✅ Found customer:', user);
        setSelectedCustomer(user);
        setShowCreateCustomer(false);
        message.success(`Tìm thấy hành khách: ${user.hoten}`);
        setCurrentStep(1); // Move to booking step
      } else {
        console.log('❌ Customer not found, show create form');
        setSelectedCustomer(null);
        setShowCreateCustomer(true);
        message.info('Không tìm thấy hành khách. Vui lòng tạo tài khoản mới.');
      }
    } catch (error: any) {
      console.error('❌ Error searching customer:', error);
      message.error('Lỗi khi tìm kiếm hành khách');
      setSelectedCustomer(null);
      setShowCreateCustomer(true);
    } finally {
      setCustomerSearchLoading(false);
    }
  };

  // Create new customer
  const createNewCustomer = async (values: { hoten: string; email?: string }) => {
    try {
      setCreateCustomerLoading(true);
      console.log('👤 Creating new customer:', { ...values, sodienthoai: customerPhone });
      
      const password = generatePassword();
      const userData = {
        hoten: values.hoten,
        sodienthoai: customerPhone.trim(),
        password: password,
        email: values.email || undefined
      };

      const newUser = await api.createUser(userData);
      console.log('✅ Created new customer:', newUser);
      
      setSelectedCustomer(newUser);
      setShowCreateCustomer(false);
      createCustomerForm.resetFields();
      
      message.success(`Tạo tài khoản thành công cho ${newUser.hoten}`);
      setCurrentStep(1); // Move to booking step
      
    } catch (error: any) {
      console.error('❌ Error creating customer:', error);
      message.error('Lỗi khi tạo tài khoản hành khách');
    } finally {
      setCreateCustomerLoading(false);
    }
  };

  // Reset customer selection
  const resetCustomerSelection = () => {
    setCustomerPhone('');
    setSelectedCustomer(null);
    setShowCreateCustomer(false);
    setCurrentStep(0);
    createCustomerForm.resetFields();
  };

  // Steps configuration
  const steps = [
    {
      title: 'Tìm hành khách',
      content: 'customer-search'
    },
    {
      title: 'Đặt vé',
      content: 'booking'
    },
    {
      title: 'Hoàn thành',
      content: 'complete'
    }
  ];

  // Create or get location by address result
  async function createLocation(address: AddressResult): Promise<number | null> {
    try {
      // Check if location already exists in DB by lat/lon (optional, if API supports)
      // Otherwise, always create new
      const locationData = {
        tendiadiem: address.display_name,
        lat: parseFloat(address.lat),
        lon: parseFloat(address.lon)
      };
      const res = await api.createLocation(locationData);
      // API should return the created location object with madiadiem
      if (res && res.madiadiem) {
        return res.madiadiem;
      }
      // Some APIs may return the whole object or just the id
      if (typeof res === 'number') {
        return res;
      }
      return null;
    } catch (error) {
      console.error('❌ Error creating location:', error);
      return null;
    }
  }

  // Calculate estimated distance between two points
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };  // Calculate total amount for all passengers
  const calculateTotalAmount = useCallback(() => {
    let totalAmount = 0;
    
    // Add price for main booker (based on main pickup/dropoff)
    const mainPrice = priceInfo?.giatien || priceInfo?.giacuoc || 0;
    totalAmount += mainPrice * mainBookerSeats;
    
    console.log('🧮 [Staff] Calculating total amount:');
    console.log('💰 Main price:', mainPrice, 'x', mainBookerSeats, '=', mainPrice * mainBookerSeats);
    
    // Add price for each additional passenger (they have their own price)
    passengers.forEach((passenger, index) => {
      const passengerPrice = passenger.priceInfo?.giatien || passenger.priceInfo?.giacuoc || mainPrice;
      const passengerAmount = passengerPrice * passenger.soghe;
      totalAmount += passengerAmount;
      
      console.log(`👤 [Staff] Passenger ${index + 1}:`, {
        name: passenger.tenkhach,
        seats: passenger.soghe,
        ownPrice: passenger.priceInfo?.giatien || passenger.priceInfo?.giacuoc,
        usedPrice: passengerPrice,
        amount: passengerAmount,
        hasPickup: !!passenger.selectedPickup,
        hasDropoff: !!passenger.selectedDropoff
      });
    });
    
    console.log('💳 [Staff] Total amount:', totalAmount);
    return totalAmount;
  }, [priceInfo, mainBookerSeats, passengers]);
  // Calculate price for a specific passenger
  const calculatePassengerPrice = async (passengerIndex: number) => {
    console.log(`🔄 [Staff] Starting price calculation for passenger ${passengerIndex}`);
    
    setPassengers(currentPassengers => {
      const passenger = currentPassengers[passengerIndex];
      if (!passenger?.selectedPickup || !passenger?.selectedDropoff) {
        console.log(`❌ [Staff] Cannot calculate price for passenger ${passengerIndex}: missing pickup/dropoff`);
        return currentPassengers;
      }

      console.log(`🔄 [Staff] Calculating price for passenger ${passengerIndex}:`, {
        name: passenger.tenkhach,
        pickup: passenger.selectedPickup.display_name,
        dropoff: passenger.selectedDropoff.display_name
      });

      // Update passenger price loading state
      const updatedPassengers = [...currentPassengers];
      updatedPassengers[passengerIndex] = { ...passenger, priceLoading: true };
      
      // Start async price calculation
      (async () => {
        try {
          const response = await api.calculatePrice({
            lat_don: passenger.selectedPickup!.lat,
            lon_don: passenger.selectedPickup!.lon,
            lat_tra: passenger.selectedDropoff!.lat,
            lon_tra: passenger.selectedDropoff!.lon,
          });

          console.log(`✅ [Staff] Price calculated for passenger ${passengerIndex}:`, response);

          // Update passenger with price info
          setPassengers(latestPassengers => {
            const finalPassengers = [...latestPassengers];
            finalPassengers[passengerIndex] = { 
              ...finalPassengers[passengerIndex], 
              priceInfo: response, 
              priceLoading: false 
            };
            console.log(`📝 [Staff] Updated passenger ${passengerIndex} with price:`, finalPassengers[passengerIndex]);
            return finalPassengers;
          });
          
        } catch (error) {
          console.error('[Staff] Error calculating passenger price:', error);
          // Update with error state
          setPassengers(latestPassengers => {
            const finalPassengers = [...latestPassengers];
            finalPassengers[passengerIndex] = { 
              ...finalPassengers[passengerIndex], 
              priceInfo: null, 
              priceLoading: false 
            };
            return finalPassengers;
          });
        }
      })();

      return updatedPassengers;
    });
  };

  // State for total amount
  const [totalAmount, setTotalAmount] = useState(0);

  // Recalculate total amount when relevant data changes
  useEffect(() => {
    const amount = calculateTotalAmount();
    setTotalAmount(amount);
  }, [calculateTotalAmount]);

  // Get selected shift info
  const selectedShiftInfo = shifts.find(shift => shift.maca === selectedShift);
  
  // Calculate estimated distance
  const estimatedDistance = selectedPickup && selectedDropoff 
    ? calculateDistance(
        parseFloat(selectedPickup.lat), 
        parseFloat(selectedPickup.lon),
        parseFloat(selectedDropoff.lat),
        parseFloat(selectedDropoff.lon)
      ).toFixed(1)
    : null;

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
      // Clear all passenger search timeouts
      Object.values(passengerSearchTimeouts).forEach(timeout => {
        if (timeout) {
          clearTimeout(timeout);
        }
      });
    };
  }, [searchTimeout, passengerSearchTimeouts]);

  // Load shifts when date changes
  const loadShifts = async (date: dayjs.Dayjs) => {
    try {
      setLoading(true);
      const dateString = date.format('YYYY-MM-DD');
      console.log('🗓️ Loading shifts for date:', dateString);
      
      const response = await api.getShiftsByCa({
        ngay: dateString
      });
      
      console.log('📋 API Response:', response);
      
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
      
      console.log('🚌 Filtered shifts data:', shiftsData);
      setShifts(shiftsData);
      
      if (shiftsData.length === 0) {
        message.info(`Không có ca xe nào trong ngày ${date.format('DD/MM/YYYY')}`);
      } else {
        message.success(`Tìm thấy ${shiftsData.length} ca xe cho ngày ${date.format('DD/MM/YYYY')}`);
      }
      
    } catch (error: any) {
      console.error('❌ Error loading shifts:', error);
      message.error(`Không thể tải ca xe cho ngày ${date.format('DD/MM/YYYY')}: ${error.message || 'Unknown error'}`);
      setShifts([]);
    } finally {
      setLoading(false);
    }
  };

  // Search address function with debounce
  const searchAddress = useCallback(async (query: string, isPickup: boolean = true) => {
    if (!query || query.length < 3) {
      return;
    }

    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    const setLoadingState = isPickup ? setPickupLoading : setDropoffLoading;
    const setOptions = isPickup ? setPickupOptions : setDropoffOptions;

    const newTimeout = setTimeout(async () => {
      try {
        setLoadingState(true);
        const response = await api.searchAddress(query);
        const results = response || [];
        const options = results.map((item: AddressResult, index: number) => ({
          value: item.display_name,
          key: `${item.place_id}-${index}`,
          data: item
        }));

        setOptions(options);
      } catch (error) {
        console.error('Error searching address:', error);
        message.error('Không thể tìm kiếm địa chỉ');
      } finally {
        setLoadingState(false);
      }
    }, 500);

    setSearchTimeout(newTimeout);
  }, [searchTimeout]);

  // Separate search function for passenger autocompletes
  const searchPassengerAddress = useCallback(async (query: string, passengerIndex: number, isPickup: boolean = true) => {
    console.log('🔍 searchPassengerAddress called:', { query, passengerIndex, isPickup });
    
    if (!query || query.length < 3) {
      console.log('❌ Query too short, skipping search:', query);
      return;
    }

    const timeoutKey = `${passengerIndex}-${isPickup ? 'pickup' : 'dropoff'}`;

    if (passengerSearchTimeouts[timeoutKey]) {
      clearTimeout(passengerSearchTimeouts[timeoutKey]);
    }

    const newTimeout = setTimeout(async () => {
      try {
        console.log(`🚀 Starting search for passenger ${passengerIndex}, ${isPickup ? 'pickup' : 'dropoff'}:`, query);
        
        if (isPickup) {
          setPassengerPickupLoading(prev => ({ ...prev, [passengerIndex]: true }));
        } else {
          setPassengerDropoffLoading(prev => ({ ...prev, [passengerIndex]: true }));
        }

        const response = await api.searchAddress(query);
        console.log(`✅ Search response for passenger ${passengerIndex}:`, response);

        const results = response || [];
        const options = results.map((item: AddressResult, index: number) => ({
          value: item.display_name,
          key: `passenger-${passengerIndex}-${isPickup ? 'pickup' : 'dropoff'}-${item.place_id}-${index}`,
          data: item
        }));

        console.log(`📝 Options created for passenger ${passengerIndex}, ${isPickup ? 'pickup' : 'dropoff'}:`, options);

        if (isPickup) {
          setPassengerPickupOptions(prev => ({ ...prev, [passengerIndex]: options }));
        } else {
          setPassengerDropoffOptions(prev => ({ ...prev, [passengerIndex]: options }));
        }
      } catch (error) {
        console.error('❌ Error searching passenger address:', error);
        message.error('Không thể tìm kiếm địa chỉ');
      } finally {
        if (isPickup) {
          setPassengerPickupLoading(prev => ({ ...prev, [passengerIndex]: false }));
        } else {
          setPassengerDropoffLoading(prev => ({ ...prev, [passengerIndex]: false }));
        }
      }
    }, 500);

    setPassengerSearchTimeouts(prev => ({ ...prev, [timeoutKey]: newTimeout }));
  }, [passengerSearchTimeouts]);

  // Get price when both addresses are selected
  const getPrice = async (pickup: AddressResult, dropoff: AddressResult) => {
    try {
      setPriceLoading(true);
      console.log('🏷️ Getting price for:', {
        pickup: pickup.display_name,
        dropoff: dropoff.display_name,
        coordinates: {
          lat_don: pickup.lat,
          lon_don: pickup.lon,
          lat_tra: dropoff.lat,
          lon_tra: dropoff.lon
        }
      });

      const response = await api.calculatePrice({
        lat_don: pickup.lat,
        lon_don: pickup.lon,
        lat_tra: dropoff.lat,
        lon_tra: dropoff.lon
      });

      console.log('💰 Price response:', response);
      
      if (response.success && response.giatien) {
        const normalizedResponse: PriceInfo = {
          success: response.success,
          giatien: response.giatien,
          giacuoc: response.giatien,
          tuyenduong: response.tuyenduong,
          huyen_don: response.huyen_don,
          huyen_tra: response.huyen_tra,
          coordinates: response.coordinates
        };
        setPriceInfo(normalizedResponse);
      } else {
        setPriceInfo({ 
          message: 'Không tìm thấy tuyến đường hoặc không thể tính giá' 
        });
      }
      
    } catch (error: any) {
      console.error('❌ Error getting price:', error);
      
      let errorMessage = 'Không thể lấy thông tin giá';
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setPriceInfo({ message: errorMessage });
    } finally {
      setPriceLoading(false);
    }
  };

  // Handle date change
  const handleDateChange = (date: dayjs.Dayjs | null) => {
    setSelectedDate(date);
    setSelectedShift(null);
    if (date) {
      loadShifts(date);
    } else {
      setShifts([]);
    }
  };

  // Handle address selection
  const handleAddressSelect = (value: string, option: any, isPickup: boolean = true) => {
    const addressData = option.data;
    if (isPickup) {
      setSelectedPickup(addressData);
      // Get price if dropoff is already selected
      if (selectedDropoff) {
        getPrice(addressData, selectedDropoff);
      }
    } else {
      setSelectedDropoff(addressData);
      // Get price if pickup is already selected
      if (selectedPickup) {
        getPrice(selectedPickup, addressData);
      }
    }
  };

  // Handle address search input change (reset selected when typing)
  const handleAddressChange = (value: string, isPickup: boolean = true) => {
    if (isPickup && selectedPickup && value !== selectedPickup.display_name) {
      setSelectedPickup(null);
      setPriceInfo(null);
    } else if (!isPickup && selectedDropoff && value !== selectedDropoff.display_name) {
      setSelectedDropoff(null);
      setPriceInfo(null);
    }
  };

  // Passenger management functions
  const addPassenger = () => {
    if (totalSeats >= 7) {
      message.warning('Số ghế tối đa là 7. Không thể thêm hành khách.');
      return;
    }
    
    setPassengers([...passengers, { 
      tenkhach: '', 
      sodienthoaikhach: '', 
      soghe: 1,
      selectedPickup: null,
      selectedDropoff: null
    }]);
  };

  const removePassenger = (index: number) => {
    const newPassengers = passengers.filter((_, i) => i !== index);
    setPassengers(newPassengers);
    updateTotalSeats(newPassengers);
    
    // Clean up options and loading states for this passenger
    setPassengerPickupOptions(prev => {
      const newOptions = { ...prev };
      delete newOptions[index];
      return newOptions;
    });
    
    setPassengerDropoffOptions(prev => {
      const newOptions = { ...prev };
      delete newOptions[index];
      return newOptions;
    });
    
    setPassengerPickupLoading(prev => {
      const newLoading = { ...prev };
      delete newLoading[index];
      return newLoading;
    });
    
    setPassengerDropoffLoading(prev => {
      const newLoading = { ...prev };
      delete newLoading[index];
      return newLoading;
    });
    
    // Clear timeouts for this passenger
    setPassengerSearchTimeouts(prev => {
      const newTimeouts = { ...prev };
      const pickupKey = `${index}-pickup`;
      const dropoffKey = `${index}-dropoff`;
      
      if (newTimeouts[pickupKey]) {
        clearTimeout(newTimeouts[pickupKey]);
        delete newTimeouts[pickupKey];
      }
      if (newTimeouts[dropoffKey]) {
        clearTimeout(newTimeouts[dropoffKey]);
        delete newTimeouts[dropoffKey];
      }
      
      return newTimeouts;
    });
  };

  const updatePassenger = (index: number, field: keyof PassengerDetail, value: any) => {
    const updatedPassengers = [...passengers];
    updatedPassengers[index] = { ...updatedPassengers[index], [field]: value };
    
    // If pickup or dropoff changed, calculate new price
    if ((field === 'selectedPickup' || field === 'selectedDropoff') && 
        updatedPassengers[index].selectedPickup && 
        updatedPassengers[index].selectedDropoff) {
      updatedPassengers[index].priceInfo = null; // Reset price while calculating
      setPassengers(updatedPassengers);
      calculatePassengerPrice(index);
    } else {
      setPassengers(updatedPassengers);
    }
  };

  const updateTotalSeats = (passengerList: PassengerDetail[], customMainSeats?: number) => {
    const passengerSeatsTotal = passengerList.reduce((sum, passenger) => sum + (passenger.soghe || 0), 0);
    const currentMainSeats = customMainSeats !== undefined ? customMainSeats : mainBookerSeats;
    const total = currentMainSeats + passengerSeatsTotal;
    console.log('🧮 Calculating total seats:', {
      mainSeats: currentMainSeats,
      passengerSeats: passengerSeatsTotal,
      total: total
    });
    setTotalSeats(total);  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>
          <UserOutlined /> Đặt vé cho hành khách (Nhân viên)
        </Title>
        
        <Steps current={currentStep} style={{ marginBottom: '32px' }}>
          {steps.map(item => (
            <Step key={item.title} title={item.title} />
          ))}
        </Steps>

        {/* Step 1: Customer Search/Create */}
        {currentStep === 0 && (
          <Card title="🔍 Tìm kiếm hành khách" style={{ marginBottom: '24px' }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Row gutter={16} align="middle">
                <Col span={16}>
                  <Input
                    size="large"
                    placeholder="Nhập số điện thoại hành khách"
                    prefix={<PhoneOutlined />}
                    value={customerPhone}
                    onChange={(e) => setCustomerPhone(e.target.value)}
                    onPressEnter={searchCustomerByPhone}
                  />
                </Col>
                <Col span={8}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<SearchOutlined />}
                    onClick={searchCustomerByPhone}
                    loading={customerSearchLoading}
                    block
                  >
                    Tìm kiếm
                  </Button>
                </Col>
              </Row>

              {selectedCustomer && (
                <Alert
                  message="Đã tìm thấy hành khách"
                  description={
                    <div>
                      <p><strong>Tên:</strong> {selectedCustomer.hoten}</p>
                      <p><strong>Số điện thoại:</strong> {selectedCustomer.sodienthoai}</p>
                      <p><strong>Email:</strong> {selectedCustomer.email || 'Chưa có'}</p>
                    </div>
                  }
                  type="success"
                  showIcon
                  action={
                    <Space>
                      <Button size="small" onClick={resetCustomerSelection}>
                        Tìm khách khác
                      </Button>
                      <Button type="primary" size="small" onClick={() => setCurrentStep(1)}>
                        Tiếp tục đặt vé
                      </Button>
                    </Space>
                  }
                />
              )}

              {showCreateCustomer && (
                <Card title="👤 Tạo tài khoản mới" style={{ backgroundColor: '#f6ffed' }}>
                  <Form
                    form={createCustomerForm}
                    layout="vertical"
                    onFinish={createNewCustomer}
                  >
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          label="Số điện thoại"
                          name="sodienthoai"
                          initialValue={customerPhone}
                        >
                          <Input disabled prefix={<PhoneOutlined />} />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item
                          label="Họ và tên"
                          name="hoten"
                          rules={[{ required: true, message: 'Vui lòng nhập họ tên' }]}
                        >
                          <Input prefix={<UserOutlined />} placeholder="Nhập họ tên hành khách" />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          label="Email (tùy chọn)"
                          name="email"
                          rules={[{ type: 'email', message: 'Email không hợp lệ' }]}
                        >
                          <Input placeholder="email@example.com" />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="Mật khẩu">
                          <Input.Password 
                            disabled 
                            placeholder="Sẽ được tạo tự động" 
                            value="••••••••" 
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Form.Item>
                      <Space>
                        <Button 
                          type="primary" 
                          htmlType="submit" 
                          loading={createCustomerLoading}
                          icon={<PlusOutlined />}
                        >
                          Tạo tài khoản và tiếp tục
                        </Button>
                        <Button onClick={() => setShowCreateCustomer(false)}>
                          Hủy
                        </Button>
                      </Space>
                    </Form.Item>
                  </Form>
                </Card>
              )}
            </Space>
          </Card>
        )}

        {/* Step 2: Booking */}
        {currentStep === 1 && selectedCustomer && (
          <Card title={`🎫 Đặt vé cho: ${selectedCustomer.hoten}`}>  
            <Form
              form={form}
              layout="vertical"
              onFinish={async (values) => {
                // Logic submit booking, dùng selectedCustomer.manguoidung
                try {
                  setLoading(true);
                  if (!selectedShift) {
                    message.error('Vui lòng chọn ca xe');
                    return;
                  }
                  if (!selectedPickup) {
                    message.error('Vui lòng chọn điểm đón');
                    return;
                  }
                  if (!selectedDropoff) {
                    message.error('Vui lòng chọn điểm trả');
                    return;
                  }
                  if (selectedPickup.place_id === selectedDropoff.place_id) {
                    message.error('Điểm đón và điểm trả không thể giống nhau');
                    return;
                  }
                  for (let i = 0; i < passengers.length; i++) {
                    const passenger = passengers[i];
                    if (!passenger.tenkhach.trim()) {
                      message.error(`Vui lòng nhập tên hành khách thứ ${i + 1}`);
                      return;
                    }
                    if (!passenger.sodienthoaikhach.trim()) {
                      message.error(`Vui lòng nhập số điện thoại hành khách thứ ${i + 1}`);
                      return;
                    }
                    if (!passenger.selectedPickup) {
                      message.error(`Vui lòng chọn điểm đón cho hành khách thứ ${i + 1}`);
                      return;
                    }
                    if (!passenger.selectedDropoff) {
                      message.error(`Vui lòng chọn điểm trả cho hành khách thứ ${i + 1}`);
                      return;
                    }
                    if (passenger.selectedPickup.place_id === passenger.selectedDropoff.place_id) {
                      message.error(`Điểm đón và điểm trả của hành khách thứ ${i + 1} không thể giống nhau`);
                      return;
                    }
                  }
                  message.loading('Đang tạo địa điểm...', 1);
                  const pickupLocationId = await createLocation(selectedPickup);
                  if (!pickupLocationId) {
                    message.error('Không thể tạo điểm đón chính');
                    return;
                  }
                  const dropoffLocationId = await createLocation(selectedDropoff);
                  if (!dropoffLocationId) {
                    message.error('Không thể tạo điểm trả chính');
                    return;
                  }
                  const processedPassengers = [];
                  for (let i = 0; i < passengers.length; i++) {
                    const passenger = passengers[i];
                    const passengerPickupId = await createLocation(passenger.selectedPickup!);
                    if (!passengerPickupId) {
                      message.error(`Không thể tạo điểm đón cho hành khách thứ ${i + 1}`);
                      return;
                    }
                    const passengerDropoffId = await createLocation(passenger.selectedDropoff!);
                    if (!passengerDropoffId) {
                      message.error(`Không thể tạo điểm trả cho hành khách thứ ${i + 1}`);
                      return;
                    }
                    processedPassengers.push({
                      tenkhach: passenger.tenkhach,
                      sodienthoaikhach: passenger.sodienthoaikhach,
                      diemdon: passengerPickupId,
                      diemtra: passengerDropoffId,
                      soghe: passenger.soghe,
                      ghichu: passenger.ghichu || `Đặt từ ${passenger.selectedPickup!.display_name} đến ${passenger.selectedDropoff!.display_name}`
                    });
                  }
                  message.loading('Đang đặt xe...', 2);                  const bookingData = {
                    maca: selectedShift,
                    diemdon: pickupLocationId,
                    diemtra: dropoffLocationId,
                    soghe: mainBookerSeats,
                    ghichu: `Đặt từ ${selectedPickup.display_name} đến ${selectedDropoff.display_name}`,
                    chitietdatxe: processedPassengers.length > 0 ? processedPassengers : undefined,
                    ma_khach: selectedCustomer.manguoidung // Mã hành khách để tạo booking
                  };
                  const bookingResponse = await api.createStaffBooking(bookingData);
                  message.success({
                    content: `Đặt xe thành công! Mã đặt xe: ${bookingResponse.madatxe}`,
                    duration: 5
                  });
                  Modal.success({
                    title: 'Đặt xe thành công!',
                    content: (
                      <div>
                        <p><strong>Mã đặt xe:</strong> {bookingResponse.madatxe}</p>
                        <p><strong>Điểm đón:</strong> {bookingResponse.diemdon.tendiadiem}</p>
                        <p><strong>Điểm trả:</strong> {bookingResponse.diemtra.tendiadiem}</p>
                        <p><strong>Thời gian xuất phát:</strong> {bookingResponse.maca.gioxuatphat} - {dayjs(bookingResponse.maca.ngayxuatphat).format('DD/MM/YYYY')}</p>
                        <p><strong>Số ghế:</strong> {bookingResponse.soghe}</p>
                        {(priceInfo?.giatien || priceInfo?.giacuoc) && <p><strong>Giá vé ước tính:</strong> {((priceInfo.giatien || priceInfo.giacuoc || 0) * totalSeats).toLocaleString()} VNĐ</p>}
                      </div>
                    ),
                    width: 500
                  });
                  form.resetFields();
                  setSelectedDate(null);
                  setSelectedShift(null);
                  setSelectedPickup(null);
                  setSelectedDropoff(null);
                  setPickupOptions([]);
                  setDropoffOptions([]);
                  setPriceInfo(null);
                  setPassengers([]);
                  setMainBookerSeats(1);
                  setTotalSeats(1);
                  setCurrentStep(2);
                } catch (error: any) {
                  let errorMessage = 'Đặt xe thất bại. Vui lòng thử lại';
                  if (error.response?.data?.error) {
                    errorMessage = error.response.data.error;
                  } else if (error.response?.data?.message) {
                    errorMessage = error.response.data.message;
                  } else if (error.message) {
                    errorMessage = error.message;
                  }
                  message.error(errorMessage);
                } finally {
                  setLoading(false);
                }
              }}
              onFinishFailed={(errorInfo) => {
                console.log('❌ Form validation failed:', errorInfo);
              }}
            >
              {/* Date and Shift Selection */}
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="ngayxuatphat"
                    label={<Space><CalendarOutlined /><span>Chọn ngày</span></Space>}
                    rules={[{ required: true, message: 'Vui lòng chọn ngày' }]}
                  >
                    <DatePicker
                      style={{ width: '100%' }}
                      format="DD/MM/YYYY"
                      placeholder="Chọn ngày xuất phát"
                      disabledDate={(current) => current && current < dayjs().startOf('day')}
                      onChange={handleDateChange}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="maca"
                    label={<Space><ClockCircleOutlined /><span>Chọn ca xe</span></Space>}
                    rules={[{ required: true, message: 'Vui lòng chọn ca xe' }]}
                  >
                    <Select
                      placeholder="Chọn ca xe"
                      loading={loading}
                      disabled={!selectedDate}
                      onChange={(value) => setSelectedShift(value)}
                      notFoundContent={selectedDate ? (loading ? <Spin size="small" /> : 'Không có ca xe') : 'Vui lòng chọn ngày trước'}
                    >
                      {shifts.map(shift => (
                        <Option key={shift.maca} value={shift.maca}>
                          <Space>
                            <Text strong>{shift.gioxuatphat}</Text>
                            <Text type="secondary">- {shift.mahuyenxuatphat.tenhuyen}</Text>
                          </Space>
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>              </Row>

              {/* Selected Shift Info */}
              {selectedShiftInfo && (
                <>
                  <Divider />
                  <Alert
                    message="Thông tin ca xe đã chọn"
                    description={
                      <div>
                        <Space direction="vertical" size="small">
                          <Text>
                            <ClockCircleOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                            <strong>Giờ xuất phát:</strong> {selectedShiftInfo.gioxuatphat}
                          </Text>
                          <Text>
                            <EnvironmentOutlined style={{ marginRight: '8px', color: '#52c41a' }} />
                            <strong>Huyện xuất phát:</strong> {selectedShiftInfo.mahuyenxuatphat.tenhuyen}
                          </Text>
                          <Text>
                            <CalendarOutlined style={{ marginRight: '8px', color: '#faad14' }} />
                            <strong>Ngày xuất phát:</strong> {dayjs(selectedShiftInfo.ngayxuatphat).format('DD/MM/YYYY')}
                          </Text>
                        </Space>
                      </div>
                    }
                    type="info"
                    showIcon
                    icon={<InfoCircleOutlined />}
                    style={{ marginBottom: '16px' }}
                  />
                </>
              )}

              <Divider />

              {/* Address Selection */}
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    label={
                      <Space>
                        <EnvironmentOutlined style={{ color: '#52c41a' }} />
                        <span>Điểm đón</span>
                      </Space>
                    }
                  >
                    <AutoComplete
                      placeholder="Nhập địa chỉ điểm đón"
                      options={pickupOptions}
                      onSearch={(value) => searchAddress(value, true)}
                      onChange={(value) => handleAddressChange(value, true)}
                      onSelect={(value, option) => handleAddressSelect(value, option, true)}
                      notFoundContent={pickupLoading ? <Spin size="small" /> : 'Không tìm thấy địa chỉ'}
                      allowClear
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} md={12}>
                  <Form.Item
                    label={
                      <Space>
                        <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                        <span>Điểm trả</span>
                      </Space>
                    }
                  >
                    <AutoComplete
                      placeholder="Nhập địa chỉ điểm trả"
                      options={dropoffOptions}
                      onSearch={(value) => searchAddress(value, false)}
                      onChange={(value) => handleAddressChange(value, false)}
                      onSelect={(value, option) => handleAddressSelect(value, option, false)}
                      notFoundContent={dropoffLoading ? <Spin size="small" /> : 'Không tìm thấy địa chỉ'}
                      allowClear
                    />
                  </Form.Item>
                </Col>
              </Row>

              {/* Selected addresses display */}
              {(selectedPickup || selectedDropoff) && (
                <>
                  <Divider />
                  <div style={{ marginBottom: '16px' }}>
                    <Text strong>Địa chỉ đã chọn:</Text>
                    {selectedPickup && (
                      <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#f6ffed', borderLeft: '3px solid #52c41a', borderRadius: '4px' }}>
                        <Text style={{ color: '#52c41a' }}>🚗 Điểm đón: </Text>
                        <Text>{selectedPickup.display_name}</Text>
                      </div>
                    )}
                    {selectedDropoff && (
                      <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#fff2f0', borderLeft: '3px solid #ff4d4f', borderRadius: '4px' }}>
                        <Text style={{ color: '#ff4d4f' }}>🏁 Điểm trả: </Text>
                        <Text>{selectedDropoff.display_name}</Text>
                      </div>
                    )}
                    {estimatedDistance && (
                      <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#f0f5ff', borderLeft: '3px solid #1890ff', borderRadius: '4px' }}>
                        <Text style={{ color: '#1890ff' }}>📏 Khoảng cách ước tính: </Text>
                        <Text strong>{estimatedDistance} km</Text>
                      </div>
                    )}
                    {priceInfo && (
                      <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#fff7e6', borderLeft: '3px solid #faad14', borderRadius: '4px' }}>
                        {priceLoading ? (
                          <Spin size="small" style={{ marginRight: '8px' }} />
                        ) : (priceInfo.giatien || priceInfo.giacuoc) ? (
                          <>
                            <Text style={{ color: '#faad14' }}>💰 Giá vé: </Text>
                            <Text strong>{(priceInfo.giatien || priceInfo.giacuoc || 0).toLocaleString()} VNĐ/khách</Text>
                            {priceInfo.tuyenduong && (
                              <div style={{ marginTop: '4px', fontSize: '12px' }}>
                                <Text type="secondary">
                                  🛣️ {priceInfo.huyen_don?.tenhuyen} → {priceInfo.huyen_tra?.tenhuyen}
                                </Text>
                              </div>
                            )}                            {totalSeats > 1 && (
                              <>
                                <br />
                                <Text style={{ color: '#faad14' }}>💰 Tổng tiền ({totalSeats} ghế): </Text>
                                <Text strong style={{ fontSize: '16px', color: '#fa8c16' }}>
                                  {totalAmount.toLocaleString()} VNĐ
                                </Text>
                              </>
                            )}
                          </>
                        ) : (
                          <Text style={{ color: '#ff4d4f' }}>⚠️ {priceInfo.message || 'Không thể tính giá cho tuyến đường này'}</Text>
                        )}
                        {/* Debug button */}
                        {selectedPickup && selectedDropoff && (
                          <div style={{ marginTop: '8px' }}>
                            <Button 
                              size="small" 
                              onClick={() => getPrice(selectedPickup, selectedDropoff)}
                              loading={priceLoading}
                            >
                              🔄 Tính lại giá
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </>
              )}

              {/* Seat and Passenger Management */}
              {selectedPickup && selectedDropoff && (priceInfo?.giatien || priceInfo?.giacuoc) && (
                <>
                  <Divider />
                  <Row gutter={16}>
                    <Col xs={24} md={6}>
                      <Form.Item
                        label={
                          <Space>
                            <UserOutlined />
                            <span>Số ghế người đặt</span>
                          </Space>
                        }
                      >
                        <InputNumber
                          min={1}
                          max={5}
                          value={mainBookerSeats}
                          style={{ width: '100%' }}
                          addonAfter="ghế"
                          onChange={(value) => {
                            const newMainSeats = value || 1;
                            setMainBookerSeats(newMainSeats);
                            // Calculate total with new main seats
                            const passengerSeatsTotal = passengers.reduce((sum, passenger) => sum + (passenger.soghe || 0), 0);
                            const newTotal = newMainSeats + passengerSeatsTotal;
                            setTotalSeats(newTotal);
                          }}
                        />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={6}>
                      <Form.Item
                        label={
                          <Space>
                            <UserOutlined />
                            <span>Tổng số ghế</span>
                            {totalSeats === 7 && <Text style={{ color: '#ff4d4f', fontSize: '12px' }}>(Tối đa)</Text>}
                          </Space>
                        }
                      >
                        <InputNumber
                          min={1}
                          max={7}
                          value={totalSeats}
                          disabled
                          style={{ width: '100%' }}
                          addonAfter="ghế"
                        />
                        <div style={{ fontSize: '11px', color: '#8c8c8c', marginTop: '4px' }}>
                          {mainBookerSeats} ghế chính + {passengers.length} hành khách ({passengers.reduce((sum, p) => sum + (p.soghe || 0), 0)} ghế)
                        </div>
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                      <Form.Item
                        label={
                          <Space>
                            <DollarOutlined />
                            <span>Tổng tiền</span>
                          </Space>
                        }
                      >                        <Input
                          value={`${totalAmount.toLocaleString()} VNĐ`}
                          disabled
                          style={{ fontWeight: 'bold', color: '#fa8c16' }}
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  {/* Additional Passengers */}
                  <div style={{ marginTop: '16px' }}>
                    <Space style={{ marginBottom: '16px' }}>
                      <Text strong>Thông tin hành khách bổ sung:</Text>
                      <Button
                        type="dashed"
                        icon={<PlusOutlined />}
                        onClick={addPassenger}
                        size="small"
                        disabled={totalSeats >= 7}
                      >
                        {totalSeats >= 7 ? 'Đã đạt tối đa' : 'Thêm hành khách'}
                      </Button>
                      {totalSeats >= 7 && (
                        <Text style={{ color: '#ff4d4f', fontSize: '12px' }}>
                          (Tối đa 7 ghế)
                        </Text>
                      )}
                    </Space>

                    {passengers.map((passenger, index) => (
                      <Card
                        key={index}
                        size="small"
                        style={{ marginBottom: '8px' }}
                        title={`Hành khách ${index + 2}`}
                        extra={
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => removePassenger(index)}
                            size="small"
                          />
                        }
                      >
                        <Row gutter={8}>
                          <Col xs={24} sm={6}>
                            <Input
                              placeholder="Họ tên"
                              value={passenger.tenkhach}
                              onChange={(e) => updatePassenger(index, 'tenkhach', e.target.value)}
                              prefix={<UserOutlined />}
                            />
                          </Col>
                          <Col xs={24} sm={6}>
                            <Input
                              placeholder="Số điện thoại"
                              value={passenger.sodienthoaikhach}
                              onChange={(e) => updatePassenger(index, 'sodienthoaikhach', e.target.value)}
                              prefix={<PhoneOutlined />}
                            />
                          </Col>
                          <Col xs={24} sm={3}>
                            <InputNumber
                              min={1}
                              max={Math.min(5, 7 - totalSeats + (passenger.soghe || 1))}
                              value={passenger.soghe || 1}
                              onChange={(value) => {
                                console.log('🎯 InputNumber onChange:', { index, value, passenger: passenger.soghe });
                                updatePassenger(index, 'soghe', value || 1);
                              }}
                              addonAfter="ghế"
                              size="small"
                              style={{ width: '100%' }}
                              precision={0}
                              step={1}
                            />
                          </Col>
                          <Col xs={24} sm={9}>
                            <Input
                              placeholder="Ghi chú"
                              value={passenger.ghichu}
                              onChange={(e) => updatePassenger(index, 'ghichu', e.target.value)}
                            />
                          </Col>
                        </Row>
                        
                        {/* Address selection for individual passenger */}
                        <Row gutter={8} style={{ marginTop: '8px' }}>
                          <Col xs={24} sm={12}>
                            <Space size="small" style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                              <EnvironmentOutlined style={{ color: '#52c41a' }} />
                              <Text style={{ fontSize: '12px', color: '#ff4d4f' }}>Điểm đón riêng <Text style={{ color: '#ff4d4f' }}>*</Text></Text>
                            </Space>
                            <AutoComplete
                              key={`pickup-${index}`}
                              placeholder="Nhập địa chỉ điểm đón riêng (bắt buộc)"
                              options={passengerPickupOptions[index] || []}
                              onSearch={(value) => searchPassengerAddress(value, index, true)}
                              onChange={(value) => {
                                // Reset selection when typing
                                if (passenger.selectedPickup && value !== passenger.selectedPickup.display_name) {
                                  updatePassenger(index, 'selectedPickup', null);
                                }
                              }}
                              onSelect={(value, option) => {
                                const addressData = option.data;
                                updatePassenger(index, 'selectedPickup', addressData);
                              }}
                              notFoundContent={passengerPickupLoading[index] ? <Spin size="small" /> : 'Không tìm thấy địa chỉ'}
                              allowClear
                              size="small"
                              style={{ width: '100%' }}
                            >
                              <Input />
                            </AutoComplete>
                            {passenger.selectedPickup && (
                              <div style={{ fontSize: '11px', color: '#52c41a', marginTop: '2px' }}>
                                ✓ {passenger.selectedPickup.display_name}
                              </div>
                            )}
                          </Col>
                          <Col xs={24} sm={12}>
                            <Space size="small" style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                              <EnvironmentOutlined style={{ color: '#ff4d4f' }} />
                              <Text style={{ fontSize: '12px', color: '#ff4d4f' }}>Điểm trả riêng <Text style={{ color: '#ff4d4f' }}>*</Text></Text>
                            </Space>
                            <AutoComplete
                              key={`dropoff-${index}`}
                              placeholder="Nhập địa chỉ điểm trả riêng (bắt buộc)"
                              options={passengerDropoffOptions[index] || []}
                              onSearch={(value) => searchPassengerAddress(value, index, false)}
                              onChange={(value) => {
                                // Reset selection when typing
                                if (passenger.selectedDropoff && value !== passenger.selectedDropoff.display_name) {
                                  updatePassenger(index, 'selectedDropoff', null);
                                }
                              }}
                              onSelect={(value, option) => {
                                const addressData = option.data;
                                updatePassenger(index, 'selectedDropoff', addressData);
                              }}
                              notFoundContent={passengerDropoffLoading[index] ? <Spin size="small" /> : 'Không tìm thấy địa chỉ'}
                              allowClear
                              size="small"
                              style={{ width: '100%' }}
                            >
                              <Input />
                            </AutoComplete>
                            {passenger.selectedDropoff && (
                              <div style={{ fontSize: '11px', color: '#ff4d4f', marginTop: '2px' }}>
                                ✓ {passenger.selectedDropoff.display_name}
                              </div>
                            )}
                          </Col>
                        </Row>
                      </Card>
                    ))}
                  </div>
                </>
              )}

              {/* Booking Summary */}
              {selectedShift && selectedPickup && selectedDropoff && (priceInfo?.giatien || priceInfo?.giacuoc) && (
                <Card style={{ marginTop: '24px', backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
                  <Title level={5} style={{ color: '#389e0d', marginBottom: '12px' }}>
                    <InfoCircleOutlined /> Tóm tắt đơn đặt xe
                  </Title>
                  <Row gutter={16}>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>🚌 Ca xe:</Text> {selectedShiftInfo?.gioxuatphat} - {dayjs(selectedShiftInfo?.ngayxuatphat).format('DD/MM/YYYY')}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>🟢 Điểm đón chính:</Text> {selectedPickup.display_name}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>🔴 Điểm trả chính:</Text> {selectedDropoff.display_name}
                      </div>
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>👥 Tổng số ghế:</Text> {totalSeats}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>💰 Giá mỗi ghế:</Text> {(priceInfo.giatien || priceInfo.giacuoc || 0).toLocaleString()} VNĐ
                      </div>                      <div style={{ marginBottom: '8px' }}>
                        <Text strong style={{ color: '#d4380d' }}>💳 Tổng tiền:</Text> 
                        <Text strong style={{ color: '#d4380d', fontSize: '16px' }}> {totalAmount.toLocaleString()} VNĐ</Text>
                      </div>
                    </Col>
                  </Row>                  {passengers.length > 0 && (
                    <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #d9f7be' }}>
                      <Text strong>Hành khách bổ sung ({passengers.length}):</Text>
                      {passengers.map((passenger, index) => (
                        <div key={index} style={{ 
                          marginTop: '8px', 
                          padding: '8px', 
                          backgroundColor: '#fafafa', 
                          borderRadius: '4px',
                          border: '1px solid #f0f0f0'
                        }}>
                          <div style={{ marginBottom: '4px' }}>
                            <Text strong>• {passenger.tenkhach || `Hành khách ${index + 2}`} ({passenger.soghe} ghế)</Text>
                          </div>
                          
                          {passenger.selectedPickup && passenger.selectedDropoff && (
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '4px' }}>
                              🟢 {passenger.selectedPickup.display_name}
                              <br />
                              🔴 {passenger.selectedDropoff.display_name}
                            </div>
                          )}
                          
                          {/* Price info for this passenger */}
                          {passenger.selectedPickup && passenger.selectedDropoff && (
                            <div style={{ fontSize: '12px' }}>
                              {passenger.priceLoading ? (
                                <div style={{ color: '#1890ff' }}>
                                  <Spin size="small" style={{ marginRight: '4px' }} />
                                  Đang tính giá...
                                </div>
                              ) : passenger.priceInfo ? (
                                <div style={{ color: '#52c41a' }}>
                                  � Giá vé: <Text strong>{(passenger.priceInfo.giatien || passenger.priceInfo.giacuoc || 0).toLocaleString()} VNĐ/ghế</Text>
                                  {passenger.soghe > 1 && (
                                    <span> = <Text strong style={{ color: '#fa8c16' }}>{((passenger.priceInfo.giatien || passenger.priceInfo.giacuoc || 0) * passenger.soghe).toLocaleString()} VNĐ</Text></span>
                                  )}
                                </div>
                              ) : (
                                <div style={{ color: '#faad14' }}>
                                  💰 Áp dụng giá chính: <Text strong>{(priceInfo?.giatien || priceInfo?.giacuoc || 0).toLocaleString()} VNĐ/ghế</Text>
                                  {passenger.soghe > 1 && (
                                    <span> = <Text strong style={{ color: '#fa8c16' }}>{((priceInfo?.giatien || priceInfo?.giacuoc || 0) * passenger.soghe).toLocaleString()} VNĐ</Text></span>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                      <div style={{ marginTop: '8px', fontSize: '11px', color: '#666' }}>
                        <Text>💡 <em>Giá vé có thể khác nhau tùy theo địa chỉ đón/trả của từng hành khách</em></Text>
                        <br />
                        <Text>💰 <em>Tổng tiền được tính theo từng tuyến đường riêng biệt</em></Text>
                      </div>
                    </div>
                  )}
                </Card>
              )}

              {/* Submit Button */}
              <Form.Item style={{ textAlign: 'center', marginTop: '32px' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={loading}
                  disabled={!selectedShift || !selectedPickup || !selectedDropoff || !(priceInfo?.giatien || priceInfo?.giacuoc)}
                  style={{ minWidth: '200px' }}
                  onClick={() => {
                    console.log('🖱️ Button clicked!');
                    console.log('🔍 Button state:', {
                      selectedShift: !!selectedShift,
                      selectedPickup: !!selectedPickup,
                      selectedDropoff: !!selectedDropoff,
                      hasPrice: !!(priceInfo?.giatien || priceInfo?.giacuoc),
                      isDisabled: !selectedShift || !selectedPickup || !selectedDropoff || !(priceInfo?.giatien || priceInfo?.giacuoc)
                    });
                  }}
                >                  <CarOutlined />
                  {(priceInfo?.giatien || priceInfo?.giacuoc)
                    ? `Đặt Xe - ${totalAmount.toLocaleString()} VNĐ`
                    : 'Đặt Xe Ngay'
                  }
                </Button>
                {!(priceInfo?.giatien || priceInfo?.giacuoc) && selectedPickup && selectedDropoff && (
                  <div style={{ marginTop: '8px', color: '#ff4d4f', fontSize: '12px' }}>
                    Vui lòng chờ tính giá hoặc chọn lại địa chỉ
                  </div>
                )}
              </Form.Item>

              {/* --- Copy UI chọn địa chỉ, ghế, hành khách, tổng kết... từ Booking.tsx --- */}
              {/* Bạn chỉ cần copy phần UI từ Booking.tsx vào đây, giữ nguyên các handler đã khai báo ở trên */}
            </Form>
            <Button onClick={() => setCurrentStep(0)} style={{ marginTop: 16 }}>
              Quay lại chọn hành khách
            </Button>
          </Card>
        )}

        {/* Step 3: Complete */}
        {currentStep === 2 && (
          <Card title="✅ Đặt vé thành công">
            <Alert
              message="Đã hoàn thành đặt vé"
              description="Vé xe đã được đặt thành công cho hành khách. Bạn có thể tiếp tục đặt vé cho hành khách khác."
              type="success"
              showIcon
              style={{ marginBottom: '16px' }}
            />
            <Space>
              <Button type="primary" onClick={() => {
                setCurrentStep(0);
                resetCustomerSelection();
              }}>
                Đặt vé cho hành khách khác
              </Button>
              <Button onClick={() => setCurrentStep(1)}>
                Đặt vé tiếp cho khách này
              </Button>
            </Space>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default StaffBooking;