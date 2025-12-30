// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'hostel.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Hostel _$HostelFromJson(Map<String, dynamic> json) => Hostel(
  id: json['id'] as String,
  name: json['name'] as String,
  code: json['code'] as String,
  hostelType: json['hostel_type'] as String,
  typeDisplay: json['type_display'] as String,
  address: json['address'] as String?,
);

Map<String, dynamic> _$HostelToJson(Hostel instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'code': instance.code,
  'hostel_type': instance.hostelType,
  'type_display': instance.typeDisplay,
  'address': instance.address,
};

HostelRoom _$HostelRoomFromJson(Map<String, dynamic> json) => HostelRoom(
  id: json['id'] as String,
  roomNumber: json['room_number'] as String,
  floor: json['floor'] as String,
  roomType: json['room_type'] as String,
  typeDisplay: json['type_display'] as String,
  capacity: (json['capacity'] as num).toInt(),
);

Map<String, dynamic> _$HostelRoomToJson(HostelRoom instance) =>
    <String, dynamic>{
      'id': instance.id,
      'room_number': instance.roomNumber,
      'floor': instance.floor,
      'room_type': instance.roomType,
      'type_display': instance.typeDisplay,
      'capacity': instance.capacity,
    };

HostelAllocation _$HostelAllocationFromJson(Map<String, dynamic> json) =>
    HostelAllocation(
      id: json['id'] as String,
      hostelDetails: Hostel.fromJson(
        json['hostel_details'] as Map<String, dynamic>,
      ),
      roomDetails: HostelRoom.fromJson(
        json['room_details'] as Map<String, dynamic>,
      ),
      allocationDate: json['allocation_date'] as String,
      status: json['status'] as String,
      statusDisplay: json['status_display'] as String,
      isActive: json['is_active'] as bool,
      bedNumber: json['bed_number'] as String?,
    );

Map<String, dynamic> _$HostelAllocationToJson(HostelAllocation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'hostel_details': instance.hostelDetails,
      'room_details': instance.roomDetails,
      'allocation_date': instance.allocationDate,
      'status': instance.status,
      'status_display': instance.statusDisplay,
      'is_active': instance.isActive,
      'bed_number': instance.bedNumber,
    };

HostelAttendance _$HostelAttendanceFromJson(Map<String, dynamic> json) =>
    HostelAttendance(
      id: json['id'] as String,
      date: json['date'] as String,
      status: json['status'] as String,
      statusDisplay: json['status_display'] as String,
      remarks: json['remarks'] as String?,
    );

Map<String, dynamic> _$HostelAttendanceToJson(HostelAttendance instance) =>
    <String, dynamic>{
      'id': instance.id,
      'date': instance.date,
      'status': instance.status,
      'status_display': instance.statusDisplay,
      'remarks': instance.remarks,
    };

Roommate _$RoommateFromJson(Map<String, dynamic> json) => Roommate(
  id: json['id'] as String,
  fullName: json['full_name'] as String,
  className: json['class'] as String?,
  photoUrl: json['photo_url'] as String?,
);

Map<String, dynamic> _$RoommateToJson(Roommate instance) => <String, dynamic>{
  'id': instance.id,
  'full_name': instance.fullName,
  'class': instance.className,
  'photo_url': instance.photoUrl,
};

HostelDetails _$HostelDetailsFromJson(Map<String, dynamic> json) =>
    HostelDetails(
      allocation: json['allocation'] == null
          ? null
          : HostelAllocation.fromJson(
              json['allocation'] as Map<String, dynamic>,
            ),
      roommates: (json['roommates'] as List<dynamic>)
          .map((e) => Roommate.fromJson(e as Map<String, dynamic>))
          .toList(),
      attendanceHistory: (json['attendance_history'] as List<dynamic>)
          .map((e) => HostelAttendance.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$HostelDetailsToJson(HostelDetails instance) =>
    <String, dynamic>{
      'allocation': instance.allocation,
      'roommates': instance.roommates,
      'attendance_history': instance.attendanceHistory,
    };
