'''
Groupings operators by types for transformers.
'''

from stringfuzz.ast import *

# Groups of replaceable_OPS operators by Function Type
# ARG_...RET 
# e.g. STR_STR_STR means takes two strings and returns a string 
STR_STR_STR     = [ConcatNode]
STR_STR_BOOL    = [ContainsNode, PrefixOfNode, SuffixOfNode]
STR_INT_STR     = [AtNode]
STR_INT         = [LengthNode, ToIntNode]
STR_STR_INT     = [IndexOfNode]
STR_STR_INT_INT = [IndexOf2Node]
STR_STR_STR_STR = [StringReplaceNode]
STR_INT_INT_STR = [SubstringNode]
INT_STR         = [FromIntNode]
STR_RX_BOOL     = [InReNode]
STR_RX          = [StrToReNode]
RX_RX_RX        = [ReConcatNode, ReUnionNode]
RX_RX           = [ReStarNode, RePlusNode]
INT_INT_RX      = [ReRangeNode]

# types with more than one inhabitant for fuzzing
REPLACEABLE_OPS = [STR_STR_BOOL, STR_INT, RX_RX_RX, RX_RX]

# all the same argument types for rotating
ALL_STR_ARGS    = STR_STR_STR_STR + STR_STR_STR + STR_STR_INT + STR_STR_BOOL + STR_INT + STR_RX
ALL_RX_ARGS     = RX_RX_RX + RX_RX
ALL_INT_ARGS    = INT_STR + INT_INT_RX

# all the same return type for cutting
STR_RET         = STR_STR_STR + STR_STR_STR_STR + INT_STR + STR_INT_STR + STR_INT_INT_STR
INT_RET         = STR_INT + STR_STR_INT + STR_STR_INT_INT
BOOL_RET        = STR_STR_BOOL + STR_RX_BOOL
RX_RET          = STR_RX + RX_RX + RX_RX_RX + INT_INT_RX
