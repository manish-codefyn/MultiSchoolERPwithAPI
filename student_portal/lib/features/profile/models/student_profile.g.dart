// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'student_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StudentProfile _$StudentProfileFromJson(Map<String, dynamic> json) =>
    StudentProfile(
      id: json['id'] as String,
      admissionNumber: json['admission_number'] as String?,
      rollNumber: json['roll_number'] as String?,
      firstName: json['first_name'] as String,
      middleName: json['middle_name'] as String?,
      lastName: json['last_name'] as String?,
      fullName: json['full_name'] as String,
      dateOfBirth: json['date_of_birth'] as String?,
      age: (json['age'] as num?)?.toInt(),
      gender: json['gender'] as String?,
      bloodGroup: json['blood_group'] as String?,
      email: json['personal_email'] as String?,
      phone: json['mobile_primary'] as String?,
      className: json['current_class_name'] as String?,
      sectionName: json['section_name'] as String?,
      photoUrl: json['photo_url'] as String?,
      status: json['status'] as String,
    );

Map<String, dynamic> _$StudentProfileToJson(StudentProfile instance) =>
    <String, dynamic>{
      'id': instance.id,
      'admission_number': instance.admissionNumber,
      'roll_number': instance.rollNumber,
      'first_name': instance.firstName,
      'middle_name': instance.middleName,
      'last_name': instance.lastName,
      'full_name': instance.fullName,
      'date_of_birth': instance.dateOfBirth,
      'age': instance.age,
      'gender': instance.gender,
      'blood_group': instance.bloodGroup,
      'personal_email': instance.email,
      'mobile_primary': instance.phone,
      'current_class_name': instance.className,
      'section_name': instance.sectionName,
      'photo_url': instance.photoUrl,
      'status': instance.status,
    };
