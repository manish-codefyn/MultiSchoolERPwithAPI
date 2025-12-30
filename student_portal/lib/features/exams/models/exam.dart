import 'package:json_annotation/json_annotation.dart';

part 'exam.g.dart';

@JsonSerializable()
class Exam {
  final String id;
  final String name;
  @JsonKey(name: 'exam_type_name')
  final String examTypeName;
  @JsonKey(name: 'class_name_display')
  final String classNameDisplay;
  @JsonKey(name: 'academic_year_display')
  final String academicYearDisplay;
  @JsonKey(name: 'start_date')
  final String startDate;
  @JsonKey(name: 'end_date')
  final String endDate;
  final String status;
  @JsonKey(name: 'is_published')
  final bool isPublished;

  Exam({
    required this.id,
    required this.name,
    required this.examTypeName,
    required this.classNameDisplay,
    required this.academicYearDisplay,
    required this.startDate,
    required this.endDate,
    required this.status,
    required this.isPublished,
  });

  factory Exam.fromJson(Map<String, dynamic> json) => _$ExamFromJson(json);
  Map<String, dynamic> toJson() => _$ExamToJson(this);
}

@JsonSerializable()
class SubjectResult {
  final String id;
  @JsonKey(name: 'subject_name')
  final String subjectName;
  @JsonKey(name: 'theory_marks')
  final String? theoryMarks;
  @JsonKey(name: 'practical_marks')
  final String? practicalMarks;
  @JsonKey(name: 'total_marks')
  final String totalMarks;
  @JsonKey(name: 'max_marks')
  final String maxMarks;
  @JsonKey(name: 'pass_marks')
  final String passMarks;
  @JsonKey(name: 'is_absent')
  final bool isAbsent;
  @JsonKey(name: 'grade_point')
  final String? gradePoint;

  SubjectResult({
    required this.id,
    required this.subjectName,
    this.theoryMarks,
    this.practicalMarks,
    required this.totalMarks,
    required this.maxMarks,
    required this.passMarks,
    required this.isAbsent,
    this.gradePoint,
  });

  factory SubjectResult.fromJson(Map<String, dynamic> json) => _$SubjectResultFromJson(json);
  Map<String, dynamic> toJson() => _$SubjectResultToJson(this);
}

@JsonSerializable()
class ExamResult {
  final String id;
  @JsonKey(name: 'exam_name')
  final String examName;
  @JsonKey(name: 'exam_type')
  final String examType;
  @JsonKey(name: 'total_marks')
  final String totalMarks;
  @JsonKey(name: 'obtained_marks')
  final String obtainedMarks;
  final String percentage;
  @JsonKey(name: 'result_status')
  final String resultStatus;
  @JsonKey(name: 'status_display')
  final String statusDisplay;
  @JsonKey(name: 'overall_grade_display')
  final String overallGradeDisplay;
  final int? rank;
  @JsonKey(name: 'is_published')
  final bool isPublished;
  @JsonKey(name: 'subject_results')
  final List<SubjectResult> subjectResults;

  ExamResult({
    required this.id,
    required this.examName,
    required this.examType,
    required this.totalMarks,
    required this.obtainedMarks,
    required this.percentage,
    required this.resultStatus,
    required this.statusDisplay,
    required this.overallGradeDisplay,
    this.rank,
    required this.isPublished,
    required this.subjectResults,
  });

  factory ExamResult.fromJson(Map<String, dynamic> json) => _$ExamResultFromJson(json);
  Map<String, dynamic> toJson() => _$ExamResultToJson(this);
}
