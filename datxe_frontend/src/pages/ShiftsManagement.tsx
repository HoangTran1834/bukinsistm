import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  TimePicker,
  message,
  Space,
  Tag,
  Divider,
  Row,
  Col,
  Tooltip,
  Badge
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  CarOutlined,
  UserOutlined,
  CalendarOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  FilterOutlined,
  ReloadOutlined,
  ClearOutlined,
  DownOutlined,
  RightOutlined,
  DeleteOutlined,
  CloseOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { SortOrder } from 'antd/es/table/interface';
import api from '../api/backend';

const { Option } = Select;
const { RangePicker } = DatePicker;

interface Shift {
  maca: number;
  mahuyenxuatphat: {
    mahuyen: number;
    tenhuyen: string;
  };
  gioxuatphat: string;
  ngayxuatphat: string;
}

interface Vehicle {
  maxe: number;
  biensoxe: string;
  loaixe: string;
  sochongoi: number;
}

interface Driver {
  mataixe: number;
  hoten: string;
}

interface District {
  mahuyen: number;
  tenhuyen: string;
}

interface ShiftDetail {
  machitietca: number;
  maca: number;
  xe_info: {
    maxe: number;
    biensoxe: string;
    loaixe: string;
    sochongoi: number;
  };
  taixe_info: {
    mataixe: number;
    hoten: string;
    sodienthoai: string;
  };
}

const ShiftsManagement: React.FC = () => {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(false);  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [assignModalVisible, setAssignModalVisible] = useState(false);
  const [selectedShift, setSelectedShift] = useState<Shift | null>(null);  const [searchText, setSearchText] = useState('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<number[]>([]);
  const [shiftDetails, setShiftDetails] = useState<Record<number, ShiftDetail[]>>({});
  
  const [createForm] = Form.useForm();
  const [assignForm] = Form.useForm();

  // Danh sách huyện
  const districts: District[] = [
    { mahuyen: 1, tenhuyen: "Tam Kỳ" },
    { mahuyen: 2, tenhuyen: "Đà Nẵng" }
  ];

  // Load data
  useEffect(() => {
    loadShifts();
    loadDrivers();
    loadVehicles();
  }, []);
  const loadShifts = async () => {
    try {
      setLoading(true);
      const response = await api.getShifts();
      setShifts(response);
      console.log('Shifts loaded:', response); // Debug log
    } catch (error: any) {
      message.error('Không thể tải danh sách ca làm việc');
      console.error('Error loading shifts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDrivers = async () => {
    try {
      const response = await api.getDrivers();
      setDrivers(response);
      console.log('Drivers loaded:', response); // Debug log
    } catch (error: any) {
      message.error('Không thể tải danh sách tài xế');
      console.error('Error loading drivers:', error);
    }
  };const loadVehicles = async () => {
    try {
      const response = await api.getVehicles();
      setVehicles(response);
      console.log('Vehicles loaded:', response); // Debug log
    } catch (error: any) {
      message.error('Không thể tải danh sách xe');
      console.error('Error loading vehicles:', error);
      
      // Log chi tiết lỗi để debug
      if (error?.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      } else if (error?.request) {
        console.error('Request error:', error.request);
      } else {
        console.error('Error message:', error?.message);
      }
    }
  };

  // Tạo ca mới
  const handleCreateShift = async (values: any) => {
    try {
      const shiftData = {
        gioxuatphat: values.gioxuatphat.format('HH:mm:ss'),
        ngayxuatphat: values.ngayxuatphat.format('YYYY-MM-DD'),
        mahuyenxuatphat_id: values.mahuyenxuatphat_id
      };

      await api.createShift(shiftData);
      message.success('Tạo ca làm việc thành công');
      setCreateModalVisible(false);
      createForm.resetFields();
      loadShifts();
    } catch (error) {
      message.error('Không thể tạo ca làm việc');
      console.error('Error creating shift:', error);
    }
  };  // Thêm tài xế và xe vào ca  const handleAssignToShift = async (values: any) => {  // Thêm tài xế và xe vào ca
  const handleAssignToShift = async (values: any) => {
    if (!selectedShift) {
      message.error('Không có ca được chọn');
      return;
    }

    // Validate dữ liệu đầu vào
    if (!values.maxe || !values.mataixe) {
      message.error('Vui lòng chọn cả tài xế và xe');
      return;
    }

    setLoading(true);
    try {
      // Reload chi tiết ca mới nhất trước khi kiểm tra
      await loadShiftDetails(selectedShift.maca);
      
      // Kiểm tra xe/tài xế đã được phân công cho ca này chưa (client-side check)
      const currentDetails = shiftDetails[selectedShift.maca] || [];
      
      const existingVehicle = currentDetails.find(detail => 
        detail.xe_info.maxe == values.maxe // Dùng == để so sánh loose
      );
      
      const existingDriver = currentDetails.find(detail => 
        detail.taixe_info.mataixe == values.mataixe // Dùng == để so sánh loose
      );

      if (existingVehicle) {
        message.error(`Xe ${existingVehicle.xe_info.biensoxe} đã được phân công cho ca này`);
        return;
      }

      if (existingDriver) {
        message.error(`Tài xế ${existingDriver.taixe_info.hoten} đã được phân công cho ca này`);
        return;
      }

      const assignData = {
        maxe: values.maxe,
        mataixe: values.mataixe
      };

      const response = await api.assignToShift(selectedShift.maca, assignData);
      
      message.success('Phân công tài xế và xe thành công');
      setAssignModalVisible(false);
      assignForm.resetFields();
      
      // Luôn load lại chi tiết ca sau khi phân công thành công
      await loadShiftDetails(selectedShift.maca);
      
      // Nếu ca chưa được expand, expand nó để hiển thị chi tiết mới
      if (!expandedRows.includes(selectedShift.maca)) {
        setExpandedRows([...expandedRows, selectedShift.maca]);
      }
      
      // Refresh danh sách ca chính để cập nhật thông tin
      loadShifts();
      
      setSelectedShift(null);
    } catch (error: any) {
      console.error('Error assigning to shift:', error);
      
      // Xử lý lỗi chi tiết từ backend
      if (error?.response?.data?.error) {
        // Hiển thị lỗi cụ thể từ backend
        message.error(`Lỗi: ${error.response.data.error}`);
      } else if (error?.response?.data?.message) {
        message.error(`Lỗi: ${error.response.data.message}`);
      } else if (error?.response?.status === 400) {
        message.error('Dữ liệu không hợp lệ. Vui lòng kiểm tra lại tài xế và xe đã chọn.');
      } else if (error?.response?.status === 500) {
        message.error('Lỗi server nội bộ. Vui lòng thử lại sau.');
      } else if (error?.message) {
        message.error(`Lỗi kết nối: ${error.message}`);
      } else {
        message.error('Không thể phân công tài xế và xe');
      }
      
      // Log chi tiết để debug
      console.error('Full error details:', {
        status: error?.response?.status,
        data: error?.response?.data,
        message: error?.message
      });
    } finally {
      setLoading(false);
    }
  };

  // Load chi tiết ca
  const loadShiftDetails = async (maca: number) => {
    try {
      const response = await api.getShiftDetails(maca);
      setShiftDetails(prev => ({
        ...prev,
        [maca]: response.data || []
      }));
    } catch (error) {
      console.error('Error loading shift details:', error);
      message.error('Không thể tải chi tiết ca');
    }
  };

  // Toggle expand/collapse
  const toggleExpand = async (maca: number) => {
    if (expandedRows.includes(maca)) {
      // Collapse
      setExpandedRows(prev => prev.filter(id => id !== maca));
    } else {
      // Expand and load details
      setExpandedRows(prev => [...prev, maca]);
      await loadShiftDetails(maca);
    }
  };

  // Xóa chi tiết ca
  const handleDeleteShiftDetail = async (maca: number, chitietca_id: number) => {
    try {
      await api.deleteShiftDetail(maca, chitietca_id);
      message.success('Xóa chi tiết ca thành công');
      // Refresh chi tiết ca
      await loadShiftDetails(maca);
    } catch (error) {
      console.error('Error deleting shift detail:', error);
      message.error('Không thể xóa chi tiết ca');
    }
  };

  // Xóa ca
  const handleDeleteShift = async (maca: number) => {
    Modal.confirm({
      title: 'Xác nhận xóa ca',
      content: `Bạn có chắc chắn muốn xóa ca ${maca}? Hành động này không thể hoàn tác.`,
      okText: 'Xóa',
      okType: 'danger',
      cancelText: 'Hủy',
      onOk: async () => {
        try {
          await api.deleteShift(maca);
          message.success('Xóa ca thành công');
          loadShifts();
          // Remove from expanded rows and details
          setExpandedRows(prev => prev.filter(id => id !== maca));
          setShiftDetails(prev => {
            const newDetails = { ...prev };
            delete newDetails[maca];
            return newDetails;
          });
        } catch (error: any) {
          console.error('Error deleting shift:', error);
          if (error?.response?.data?.error) {
            message.error(error.response.data.error);
          } else {
            message.error('Không thể xóa ca');
          }
        }
      }
    });
  };// Filter data based on search and date range
  const filteredShifts = shifts.filter((shift) => {
    // Text search - chỉ tìm kiếm theo mã ca (số)
    const matchesSearch = searchText === '' || 
      shift.maca.toString().includes(searchText);
    
    // Date range filter
    const shiftDate = dayjs(shift.ngayxuatphat);
    const matchesDateRange = !dateRange || 
      !dateRange[0] || !dateRange[1] ||
      (shiftDate.isAfter(dateRange[0].subtract(1, 'day')) &&
       shiftDate.isBefore(dateRange[1].add(1, 'day')));
    
    // District filter
    const matchesDistrict = !selectedDistrict || 
      shift.mahuyenxuatphat.tenhuyen === selectedDistrict;
    
    return matchesSearch && matchesDateRange && matchesDistrict;
  });// Columns cho bảng ca làm việc
  const sortDirections: SortOrder[] = ['ascend', 'descend'];
  
  const shiftColumns = [
    {
      title: '',
      key: 'expand',
      width: 50,
      render: (_: any, record: Shift) => (
        <Button
          type="text"
          size="small"
          icon={expandedRows.includes(record.maca) ? <DownOutlined /> : <RightOutlined />}
          onClick={() => toggleExpand(record.maca)}
        />
      )
    },
    {
      title: 'Mã ca',
      dataIndex: 'maca',
      key: 'maca',
      width: 100,
      render: (maca: number) => <Tag color="blue">CA-{maca}</Tag>,
      sorter: (a: Shift, b: Shift) => a.maca - b.maca,
      sortDirections: sortDirections,
      showSorterTooltip: {
        title: 'Sắp xếp theo mã ca'
      },
    },
    {
      title: 'Huyện xuất phát',
      dataIndex: 'mahuyenxuatphat',
      key: 'mahuyenxuatphat',
      width: 160,
      render: (huyen: any) => (
        <Tag color="green">{huyen.tenhuyen}</Tag>
      ),
      filters: [
        { text: 'Tam Kỳ', value: 'Tam Kỳ' },
        { text: 'Đà Nẵng', value: 'Đà Nẵng' },
      ],
      filterMultiple: false,
      onFilter: (value: any, record: Shift) => 
        record.mahuyenxuatphat.tenhuyen === value,
      sorter: (a: Shift, b: Shift) => 
        a.mahuyenxuatphat.tenhuyen.localeCompare(b.mahuyenxuatphat.tenhuyen),
      sortDirections: sortDirections,
      showSorterTooltip: {
        title: 'Sắp xếp theo huyện'
      },
    },
    {
      title: 'Ngày xuất phát',
      dataIndex: 'ngayxuatphat',
      key: 'ngayxuatphat',
      width: 140,
      render: (date: string) => (
        <Tag color="purple">📅 {dayjs(date).format('DD/MM/YYYY')}</Tag>
      ),
      sorter: (a: Shift, b: Shift) => {
        const dateA = dayjs(a.ngayxuatphat);
        const dateB = dayjs(b.ngayxuatphat);
        return dateA.isBefore(dateB) ? -1 : dateA.isAfter(dateB) ? 1 : 0;
      },
      defaultSortOrder: 'ascend' as const,
      sortDirections: sortDirections,
      showSorterTooltip: {
        title: 'Sắp xếp theo ngày'
      },
    },
    {
      title: 'Giờ xuất phát',
      dataIndex: 'gioxuatphat',
      key: 'gioxuatphat',
      width: 130,
      render: (time: string) => (
        <Tag color="orange">🕐 {time}</Tag>
      ),
      sorter: (a: Shift, b: Shift) => {
        const timeA = dayjs(`2000-01-01 ${a.gioxuatphat}`);
        const timeB = dayjs(`2000-01-01 ${b.gioxuatphat}`);
        return timeA.isBefore(timeB) ? -1 : timeA.isAfter(timeB) ? 1 : 0;
      },
      defaultSortOrder: 'ascend' as const,
      sortDirections: sortDirections,
      showSorterTooltip: {
        title: 'Sắp xếp theo giờ'
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 200,
      render: (_: any, record: Shift) => (
        <Space>          <Button
            type="primary"
            size="small"
            icon={<UserOutlined />}
            onClick={async () => {
              setSelectedShift(record);
              setAssignModalVisible(true);
              // Load chi tiết ca để kiểm tra xe/tài xế đã được phân công
              await loadShiftDetails(record.maca);
            }}
          >
            Phân công
          </Button>
          <Button
            type="primary"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteShift(record.maca)}
          >
            Xóa ca
          </Button>
        </Space>      )
    }
  ];

  // Render expanded row với bảng chi tiết
  const renderExpandedRow = (record: Shift) => {
    const details = shiftDetails[record.maca] || [];
    
    if (details.length === 0) {
      return (
        <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
          <CarOutlined style={{ marginRight: 8 }} />
          Chưa có chi tiết ca nào. Hãy phân công tài xế và xe cho ca này.
        </div>
      );
    }

    const detailColumns = [
      {
        title: 'ID Chi tiết',
        dataIndex: 'machitietca',
        key: 'machitietca',
        width: 100,
        render: (id: number) => <Tag color="cyan">#{id}</Tag>
      },
      {
        title: 'Tài xế',
        dataIndex: 'taixe_info',
        key: 'taixe_info',
        width: 200,
        render: (taixe: any) => (
          <div>
            <div><strong>{taixe.hoten}</strong></div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              📞 {taixe.sodienthoai} | ID: {taixe.mataixe}
            </div>
          </div>
        )
      },
      {
        title: 'Xe',
        dataIndex: 'xe_info',
        key: 'xe_info',
        width: 200,
        render: (xe: any) => (
          <div>
            <div><strong>{xe.biensoxe}</strong></div>
            <div style={{ color: '#666', fontSize: '12px' }}>
              {xe.loaixe} - {xe.sochongoi} chỗ ngồi
            </div>
          </div>
        )
      },
      {
        title: 'Thao tác',
        key: 'actions',
        width: 100,
        render: (_: any, detailRecord: ShiftDetail) => (
          <Button
            type="primary"
            danger
            size="small"
            icon={<CloseOutlined />}
            onClick={() => handleDeleteShiftDetail(record.maca, detailRecord.machitietca)}
            title="Xóa chi tiết ca"
          >
            Xóa
          </Button>
        )
      }
    ];

    return (
      <div style={{ margin: '16px 0', background: '#fafafa', borderRadius: '8px', padding: '16px' }}>
        <div style={{ marginBottom: '12px', fontWeight: 600, color: '#1890ff' }}>
          📋 Chi tiết ca CA-{record.maca} ({details.length} phân công)
        </div>
        <Table
          columns={detailColumns}
          dataSource={details}
          rowKey="machitietca"
          pagination={false}
          size="small"
          bordered
        />
      </div>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <CalendarOutlined />
            <span>Quản lý ca làm việc</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            Tạo ca mới
          </Button>        }
      >        {/* Filters - Excel-style */}
        <Row gutter={16} style={{ marginBottom: 20 }}>
          <Col xs={24} sm={12} md={6}>            <Space direction="vertical" style={{ width: '100%' }}>
              <span style={{ fontWeight: 600, color: '#1890ff' }}>🔍 Tìm kiếm mã ca</span>
              <Input.Search
                placeholder="Nhập số mã ca..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onSearch={(value) => setSearchText(value)}
                allowClear
                style={{ width: '100%' }}
                size="middle"
              />
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span style={{ fontWeight: 600, color: '#722ed1' }}>📅 Khoảng ngày</span>
              <RangePicker
                placeholder={['Từ ngày', 'Đến ngày']}
                format="DD/MM/YYYY"
                value={dateRange}
                onChange={(dates) => setDateRange(dates)}
                allowClear
                style={{ width: '100%' }}
                size="middle"
              />
            </Space>
          </Col>          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span style={{ fontWeight: 600, color: '#52c41a' }}>🏙️ Huyện xuất phát</span>
              <Select
                placeholder="Chọn huyện"
                value={selectedDistrict}
                onChange={(value) => setSelectedDistrict(value)}
                allowClear
                style={{ width: '100%' }}
                size="middle"
              >
                <Option value="Tam Kỳ">🏙️ Tam Kỳ</Option>
                <Option value="Đà Nẵng">🌊 Đà Nẵng</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span style={{ fontWeight: 600, color: '#fa8c16' }}>🎯 Thao tác nhanh</span>
              <Space>
                <Tooltip title="Xóa tất cả bộ lọc">
                  <Button 
                    icon={<ClearOutlined />}
                    onClick={() => {
                      setSearchText('');
                      setDateRange(null);
                      setSelectedDistrict(null);
                    }}
                    size="middle"
                  >
                    Xóa bộ lọc
                  </Button>
                </Tooltip>
                <Tooltip title="Tải lại dữ liệu">
                  <Button 
                    icon={<ReloadOutlined />}
                    onClick={loadShifts}
                    type="primary"
                    ghost
                    size="middle"
                  >
                    Tải lại
                  </Button>
                </Tooltip>
              </Space>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span style={{ fontWeight: 600, color: '#13c2c2' }}>📊 Thống kê</span>
              <div style={{ 
                padding: '8px 12px', 
                background: 'linear-gradient(45deg, #f0f9ff, #e6f7ff)',
                borderRadius: 6,
                border: '1px solid #b5f5ec'
              }}>
                <Space>
                  <Badge count={filteredShifts.length} style={{ backgroundColor: '#52c41a' }} />
                  <span style={{ color: '#595959' }}>ca làm việc</span>
                </Space>
              </div>
            </Space>
          </Col>
        </Row>        <Table
          columns={shiftColumns}
          dataSource={filteredShifts}
          rowKey="maca"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} trong tổng ${total} ca làm việc`,
            pageSizeOptions: ['5', '10', '20', '50']
          }}
          size="middle"
          bordered
          scroll={{ x: 1000 }}
          sortDirections={['ascend', 'descend', 'ascend']}
          showSorterTooltip={{
            title: 'Click để sắp xếp, Shift+Click để sắp xếp nhiều cột'
          }}
          expandable={{
            expandedRowKeys: expandedRows,
            onExpand: (expanded, record) => {
              if (expanded) {
                toggleExpand(record.maca);
              } else {
                setExpandedRows(prev => prev.filter(id => id !== record.maca));
              }
            },
            expandedRowRender: renderExpandedRow,
            showExpandColumn: false, // Ẩn cột expand mặc định vì ta đã tự tạo
            expandRowByClick: false
          }}
        />
      </Card>

      {/* Modal tạo ca mới */}
      <Modal
        title="Tạo ca làm việc mới"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          createForm.resetFields();
        }}
        onOk={createForm.submit}
        width={500}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreateShift}
        >
          <Form.Item
            name="mahuyenxuatphat_id"
            label="Huyện xuất phát"
            rules={[{ required: true, message: 'Vui lòng chọn huyện xuất phát' }]}
          >
            <Select placeholder="Chọn huyện xuất phát">
              {districts.map(district => (
                <Option key={district.mahuyen} value={district.mahuyen}>
                  {district.tenhuyen}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="ngayxuatphat"
            label="Ngày xuất phát"
            rules={[{ required: true, message: 'Vui lòng chọn ngày xuất phát' }]}
          >
            <DatePicker
              style={{ width: '100%' }}
              format="DD/MM/YYYY"
              placeholder="Chọn ngày xuất phát"
            />
          </Form.Item>

          <Form.Item
            name="gioxuatphat"
            label="Giờ xuất phát"
            rules={[{ required: true, message: 'Vui lòng chọn giờ xuất phát' }]}
          >
            <TimePicker
              style={{ width: '100%' }}
              format="HH:mm"
              placeholder="Chọn giờ xuất phát"
            />
          </Form.Item>
        </Form>
      </Modal>      {/* Modal phân công tài xế và xe */}
      <Modal
        title={`Phân công cho ca ${selectedShift?.maca ? `CA-${selectedShift.maca}` : ''}`}
        open={assignModalVisible}
        onCancel={() => {
          setAssignModalVisible(false);
          assignForm.resetFields();
          setSelectedShift(null);
        }}        onOk={async () => {
          try {
            // First validate fields
            const values = await assignForm.validateFields();
            
            // Then call the handler
            await handleAssignToShift(values);
          } catch (validationError: any) {
            // Check if it's a validation error or actual error
            if (validationError.errorFields) {
              message.error('Vui lòng chọn cả tài xế và xe');
            } else {
              // It's an actual error from handleAssignToShift
              console.error('Handling error:', validationError);
            }
          }
        }}
        confirmLoading={loading}
        width={500}
        okText="Phân công"
        cancelText="Hủy"
      >{selectedShift && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ padding: 12, backgroundColor: '#f5f5f5', borderRadius: 4, marginBottom: 12 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <strong>Mã ca:</strong> CA-{selectedShift.maca}
                </Col>
                <Col span={8}>
                  <strong>Huyện:</strong> {selectedShift.mahuyenxuatphat.tenhuyen}
                </Col>
                <Col span={8}>
                  <strong>Thời gian:</strong> {selectedShift.gioxuatphat} - {dayjs(selectedShift.ngayxuatphat).format('DD/MM/YYYY')}
                </Col>
              </Row>
            </div>
            
            {/* Hiển thị xe/tài xế đã được phân công */}
            {shiftDetails[selectedShift.maca] && shiftDetails[selectedShift.maca].length > 0 && (
              <div style={{ padding: 12, backgroundColor: '#e6f7ff', borderRadius: 4, marginBottom: 12 }}>
                <div style={{ fontWeight: 600, marginBottom: 8, color: '#1890ff' }}>
                  🚗 Đã phân công ({shiftDetails[selectedShift.maca].length} cặp xe-tài xế):
                </div>
                {shiftDetails[selectedShift.maca].map((detail, index) => (
                  <div key={detail.machitietca} style={{ fontSize: '12px', marginBottom: 4 }}>
                    • <strong>{detail.xe_info.biensoxe}</strong> - {detail.taixe_info.hoten}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}        <Form
          form={assignForm}
          layout="vertical"
          onFinish={handleAssignToShift}
          onFinishFailed={(errorInfo) => {
            message.error('Vui lòng điền đầy đủ thông tin');
          }}
          validateTrigger="onSubmit"
        ><Form.Item
            name="mataixe"
            label="Tài xế"
            rules={[{ required: true, message: 'Vui lòng chọn tài xế' }]}
            validateStatus=""
          >            <Select 
              placeholder="Chọn tài xế"
              showSearch
              allowClear
              filterOption={(input, option) =>
                (option?.children?.toString().toLowerCase() ?? '').includes(input.toLowerCase())
              }              onChange={(value) => {
                // Force update form to ensure value is set
                assignForm.setFieldsValue({ mataixe: value });
              }}
            >
              {drivers.map(driver => (
                <Option key={driver.mataixe} value={driver.mataixe}>
                  {driver.hoten} (ID: {driver.mataixe})
                </Option>
              ))}
            </Select>
          </Form.Item>          <Form.Item
            name="maxe"
            label="Xe"
            rules={[{ required: true, message: 'Vui lòng chọn xe' }]}
            validateStatus=""
          >
            <Select 
              placeholder="Chọn xe"
              showSearch
              allowClear
              filterOption={(input, option) =>
                (option?.children?.toString().toLowerCase() ?? '').includes(input.toLowerCase())
              }              onChange={(value) => {
                // Force update form to ensure value is set
                assignForm.setFieldsValue({ maxe: value });
              }}
            >
              {vehicles.map(vehicle => (
                <Option key={vehicle.maxe} value={vehicle.maxe}>
                  {vehicle.biensoxe} - {vehicle.loaixe} ({vehicle.sochongoi} chỗ)
                </Option>
              ))}
            </Select>          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ShiftsManagement;
