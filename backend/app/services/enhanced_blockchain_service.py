"""
Enhanced Blockchain Service with Additional Features
Extends the basic blockchain service with Sri Lankan certificate-specific functionality
"""

from blockchain_service import BlockchainService
from typing import Dict, List


class EnhancedBlockchainService(BlockchainService):
    """
    Enhanced blockchain service with certificate-specific features
    """
    
    # O/L Grade mappings
    OL_GRADES = ['A', 'B', 'C', 'S', 'F']
    
    # A/L Grade mappings
    AL_GRADES = ['A', 'B', 'C', 'S', 'F']
    
    # A/L Streams
    AL_STREAMS = ['Physical Science', 'Biological Science', 'Commerce', 'Arts', 'Technology']
    
    def register_ol_certificate(
        self,
        document_content: bytes,
        student_address: str,
        student_index: str,
        exam_year: int,
        subjects: Dict[str, str],  # {'Mathematics': 'A', 'Science': 'B', ...}
        ipfs_hash: str = ""
    ) -> Dict:
        """
        Register an O/L certificate with subject grades
        
        Args:
            document_content: Certificate PDF/image content as bytes
            student_address: Student's Ethereum address
            student_index: Student index number (e.g., "2023OL123456")
            exam_year: Year of examination
            subjects: Dictionary of subject -> grade
            ipfs_hash: Optional IPFS hash for metadata
            
        Returns:
            Registration result
        """
        # Calculate document hash
        doc_hash = self.calculate_content_hash(document_content)
        
        # Format subject information
        subject_info = self._format_subjects(subjects)
        
        # Register on blockchain
        return self.register_document(
            document_hash=doc_hash,
            ipfs_hash=ipfs_hash or f"ol:{student_index}:{exam_year}",
            owner_address=student_address,
            document_type="O/L",
            student_index=student_index,
            exam_year=exam_year,
            exam_subject=subject_info
        )
    
    def register_al_certificate(
        self,
        document_content: bytes,
        student_address: str,
        student_index: str,
        exam_year: int,
        stream: str,
        subjects: Dict[str, str],  # {'Combined Mathematics': 'A', 'Physics': 'B', ...}
        ipfs_hash: str = ""
    ) -> Dict:
        """
        Register an A/L certificate with stream and subject grades
        
        Args:
            document_content: Certificate PDF/image content as bytes
            student_address: Student's Ethereum address
            student_index: Student index number (e.g., "2023AL789012")
            exam_year: Year of examination
            stream: A/L stream (Physical Science, Biological Science, etc.)
            subjects: Dictionary of subject -> grade
            ipfs_hash: Optional IPFS hash for metadata
            
        Returns:
            Registration result
        """
        # Validate stream
        if stream not in self.AL_STREAMS:
            return {
                'success': False,
                'error': f'Invalid stream. Must be one of: {", ".join(self.AL_STREAMS)}'
            }
        
        # Calculate document hash
        doc_hash = self.calculate_content_hash(document_content)
        
        # Format subject information with stream
        subject_info = f"{stream} | {self._format_subjects(subjects)}"
        
        # Register on blockchain
        return self.register_document(
            document_hash=doc_hash,
            ipfs_hash=ipfs_hash or f"al:{student_index}:{exam_year}",
            owner_address=student_address,
            document_type="A/L",
            student_index=student_index,
            exam_year=exam_year,
            exam_subject=subject_info
        )
    
    def verify_certificate_with_details(self, document_content: bytes) -> Dict:
        """
        Verify a certificate and return parsed details including grades
        
        Args:
            document_content: Certificate content as bytes
            
        Returns:
            Verification result with parsed details
        """
        # Calculate hash
        doc_hash = self.calculate_content_hash(document_content)
        
        # Verify on blockchain
        result = self.verify_document(doc_hash)
        
        if not result['exists']:
            return result
        
        # Parse subject information
        subject_str = result.get('exam_subject', '')
        
        if result['document_type'] == 'A/L':
            # Parse A/L format: "Stream | Subject1:Grade1, Subject2:Grade2"
            parts = subject_str.split(' | ')
            stream = parts[0] if len(parts) > 0 else ''
            subjects_str = parts[1] if len(parts) > 1 else ''
            
            result['stream'] = stream
            result['subjects'] = self._parse_subjects(subjects_str)
        else:
            # Parse O/L format: "Subject1:Grade1, Subject2:Grade2"
            result['subjects'] = self._parse_subjects(subject_str)
        
        return result
    
    def get_student_certificates_by_index(self, student_index: str) -> List[Dict]:
        """
        Get all certificates for a student using their index number
        
        Args:
            student_index: Student's index number
            
        Returns:
            List of certificate details
        """
        try:
            # Get document hash from student index
            doc_hash = self.contract.functions.getDocumentByIndex(student_index).call()
            
            if not doc_hash:
                return []
            
            # Get document details
            result = self.verify_document(doc_hash)
            
            if result['exists']:
                return [result]
            
            return []
            
        except Exception as e:
            print(f"Error getting certificates by index: {e}")
            return []
    
    def validate_grades(self, grades: Dict[str, str], certificate_type: str) -> Dict:
        """
        Validate subject grades
        
        Args:
            grades: Dictionary of subject -> grade
            certificate_type: "O/L" or "A/L"
            
        Returns:
            Validation result
        """
        valid_grades = self.OL_GRADES if certificate_type == "O/L" else self.AL_GRADES
        invalid_grades = []
        
        for subject, grade in grades.items():
            if grade.upper() not in valid_grades:
                invalid_grades.append((subject, grade))
        
        if invalid_grades:
            return {
                'valid': False,
                'message': f'Invalid grades found: {invalid_grades}',
                'valid_grades': valid_grades
            }
        
        return {
            'valid': True,
            'message': 'All grades are valid'
        }
    
    def calculate_ol_pass_status(self, subjects: Dict[str, str]) -> Dict:
        """
        Calculate O/L pass status (simplified version)
        
        Args:
            subjects: Dictionary of subject -> grade
            
        Returns:
            Pass status information
        """
        passes = sum(1 for grade in subjects.values() if grade.upper() in ['A', 'B', 'C', 'S'])
        total = len(subjects)
        
        # Simplified: Pass if 6 or more subjects with C or above
        passed = passes >= 6
        
        return {
            'passed': passed,
            'passes': passes,
            'total': total,
            'pass_rate': f"{passes}/{total}",
            'message': 'Passed' if passed else 'Failed'
        }
    
    def calculate_al_zscore(self, subjects: Dict[str, str]) -> Dict:
        """
        Placeholder for Z-score calculation
        (Actual calculation requires normalized marks from exam department)
        
        Args:
            subjects: Dictionary of subject -> grade
            
        Returns:
            Z-score information (placeholder)
        """
        # This is a simplified placeholder
        # Real Z-score calculation requires raw marks and statistical data
        
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'S': 1.0, 'F': 0.0}
        
        points = [grade_points.get(grade.upper(), 0) for grade in subjects.values()]
        avg = sum(points) / len(points) if points else 0
        
        # Rough approximation (NOT actual Z-score!)
        estimated_zscore = avg * 0.5
        
        return {
            'estimated_zscore': round(estimated_zscore, 4),
            'average_grade_point': round(avg, 2),
            'note': 'This is an estimation. Actual Z-score requires official calculation.',
            'subjects_count': len(subjects)
        }
    
    @staticmethod
    def _format_subjects(subjects: Dict[str, str]) -> str:
        """Format subjects dictionary to string"""
        return ', '.join([f"{subj}:{grade}" for subj, grade in subjects.items()])
    
    @staticmethod
    def _parse_subjects(subjects_str: str) -> Dict[str, str]:
        """Parse subjects string to dictionary"""
        if not subjects_str:
            return {}
        
        subjects = {}
        pairs = subjects_str.split(', ')
        
        for pair in pairs:
            if ':' in pair:
                subj, grade = pair.split(':', 1)
                subjects[subj] = grade
        
        return subjects


# Singleton instance
_enhanced_blockchain_service = None

def get_enhanced_blockchain_service() -> EnhancedBlockchainService:
    """Get or create enhanced blockchain service singleton"""
    global _enhanced_blockchain_service
    if _enhanced_blockchain_service is None:
        _enhanced_blockchain_service = EnhancedBlockchainService()
    return _enhanced_blockchain_service


# Example usage:
if __name__ == "__main__":
    # This is just an example - shows how to use the enhanced service
    
    print("Enhanced Blockchain Service Example")
    print("=" * 50)
    
    # Initialize service
    blockchain = get_enhanced_blockchain_service()
    
    # Example: Register O/L certificate
    ol_subjects = {
        'Mathematics': 'A',
        'Science': 'B',
        'English': 'A',
        'Sinhala': 'B',
        'History': 'C',
        'Geography': 'B',
        'Commerce': 'A',
        'Buddhism': 'S',
        'ICT': 'A'
    }
    
    # Validate grades
    validation = blockchain.validate_grades(ol_subjects, "O/L")
    print(f"Grade validation: {validation}")
    
    # Calculate pass status
    pass_status = blockchain.calculate_ol_pass_status(ol_subjects)
    print(f"O/L Pass status: {pass_status}")
    
    # Example: A/L grades
    al_subjects = {
        'Combined Mathematics': 'A',
        'Physics': 'B',
        'Chemistry': 'A'
    }
    
    # Calculate estimated Z-score
    zscore_info = blockchain.calculate_al_zscore(al_subjects)
    print(f"A/L Z-score info: {zscore_info}")
