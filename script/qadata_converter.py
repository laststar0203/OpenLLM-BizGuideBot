"""
아래 요구사항을 만족하는 QNA csv 변환 파이썬 코드를 만들어주세요

- 초기 입력으로 Q, A, input_file, save_file 세 가지의 매개변수를 받습니다. Q는 csv의 질문 컬럼, A는 csv의 답변 컬럼, input_file은 입력 csv 파일 경로, save_file은 출력 csv 파일 경로를 의미합니다.
- 세 가지의 매개변수는 어느 하나라도 입력이 안된 경우 실행하지 말고 사용자에게 필수 파라미터 조건을 알려주세요
- 입력이 정상적으로 완료되었으면 input_file 파라미터의 csv 파일 경로를 읽고 아래 예시에 맞는 전처리 작업을 수행합니다. 

example: 아래는 데이터프레임을 어떻게 변환하는지에 대한 예제입니다.

BEFORE:
Q | A
안녕|완료
기가|막혀

AFTER
text
<s>[INST] 안녕 [/INST] 완료 </s>
<s>[INST] 기가 [/INST] 막혀 </s>

- 데이터프레임 전처리 작업이 성공하였으면 인코딩은 utf-8f로 하고 인덱스를 제거하여 실행 매개변수인 save_file 에 저장해주세요

"""

import pandas as pd
import argparse
import sys

def convert_qna_to_csv(Q, A, input_file, save_file):
    # 필수 파라미터 체크
    if not all([Q, A, input_file, save_file]):
        print("필수 파라미터가 모두 입력되지 않았습니다. 아래의 입력 예시를 참고하여 다시 입력해주세요.")
        print("예시: python script.py --Q Q --A A --input_file input.csv --save_file output.csv")
        sys.exit(1)
    
    try:
        # 입력 CSV 파일 읽기
        df = pd.read_csv(input_file)
        
        # Q와 A 컬럼이 존재하는지 확인
        if Q not in df.columns or A not in df.columns:
            print(f"'{Q}' 또는 '{A}' 컬럼이 CSV 파일에 존재하지 않습니다.")
            sys.exit(1)
        
        # 데이터프레임 전처리
        df['text'] = df.apply(lambda row: f"<s>[INST] {row[Q].strip()} [/INST] {row[A].strip()} </s>", axis=1)
        
        # 결과 저장 (utf-8로 인코딩, 인덱스 제거)
        df[['text']].to_csv(save_file, index=False, encoding='utf-8')
        print(f"파일이 성공적으로 저장되었습니다: {save_file}")
    
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        sys.exit(1)

def main():
    # argparse 설정
    parser = argparse.ArgumentParser(description="Q&A CSV 파일을 전처리하여 새로운 CSV 파일로 저장하는 스크립트입니다.")
    parser.add_argument('--Q', required=True, help='질문 컬럼 이름')
    parser.add_argument('--A', required=True, help='답변 컬럼 이름')
    parser.add_argument('--input_file', required=True, help='입력 CSV 파일 경로')
    parser.add_argument('--save_file', required=True, help='저장할 CSV 파일 경로')

    args = parser.parse_args()

    # 함수 호출
    convert_qna_to_csv(args.Q, args.A, args.input_file, args.save_file)

if __name__ == '__main__':
    main()
