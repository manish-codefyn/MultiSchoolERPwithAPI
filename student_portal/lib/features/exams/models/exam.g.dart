// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'exam.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Exam _$ExamFromJson(Map<String, dynamic> json) => Exam(
  id: json['id'] as String,
  name: json['name'] as String,
  examTypeName: json['exam_type_name'] as String,
  classNameDisplay: json['class_name_display'] as String,
  academicYearDisplay: json['academic_year_display'] as String,
  startDate: json['start_date'] as String,
  endDate: json['end_date'] as String,
  status: json['status'] as String,
  isPublished: json['is_published'] as bool,
);

Map<String, dynamic> _$ExamToJson(Exam instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'exam_type_name': instance.examTypeName,
  'class_name_display': instance.classNameDisplay,
  'academic_year_display': instance.academicYearDisplay,
  'start_date': instance.startDate,
  'end_date': instance.endDate,
  'status': instance.status,
  'is_published': instance.isPublished,
};

SubjectResult _$SubjectResultFromJson(Map<String, dynamic> json) =>
    SubjectResult(
      id: json['id'] as String,
      subjectName: json['subject_name'] as String,
      theoryMarks: json['theory_marks'] as String?,
      practicalMarks: json['practical_marks'] as String?,
      totalMarks: json['total_marks'] as String,
      maxMarks: json['max_marks'] as String,
      passMarks: json['pass_marks'] as String,
      isAbsent: json['is_absent'] as bool,
      gradePoint: json['grade_point'] as String?,
    );

Map<String, dynamic> _$SubjectResultToJson(SubjectResult instance) =>
    <String, dynamic>{
      'id': instance.id,
      'subject_name': instance.subjectName,
      'theory_marks': instance.theoryMarks,
      'practical_marks': instance.practicalMarks,
      'total_marks': instance.totalMarks,
      'max_marks': instance.maxMarks,
      'pass_marks': instance.passMarks,
      'is_absent': instance.isAbsent,
      'grade_point': instance.gradePoint,
    };

ExamResult _$ExamResultFromJson(Map<String, dynamic> json) => ExamResult(
  id: json['id'] as String,
  examName: json['exam_name'] as String,
  examType: json['exam_type'] as String,
  totalMarks: json['total_marks'] as String,
  obtainedMarks: json['obtained_marks'] as String,
  percentage: json['percentage'] as String,
  resultStatus: json['result_status'] as String,
  statusDisplay: json['status_display'] as String,
  overallGradeDisplay: json['overall_grade_display'] as String,
  rank: (json['rank'] as num?)?.toInt(),
  isPublished: json['is_published'] as bool,
  subjectResults: (json['subject_results'] as List<dynamic>)
      .map((e) => SubjectResult.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$ExamResultToJson(ExamResult instance) =>
    <String, dynamic>{
      'id': instance.id,
      'exam_name': instance.examName,
      'exam_type': instance.examType,
      'total_marks': instance.totalMarks,
      'obtained_marks': instance.obtainedMarks,
      'percentage': instance.percentage,
      'result_status': instance.resultStatus,
      'status_display': instance.statusDisplay,
      'overall_grade_display': instance.overallGradeDisplay,
      'rank': instance.rank,
      'is_published': instance.isPublished,
      'subject_results': instance.subjectResults,
    };
