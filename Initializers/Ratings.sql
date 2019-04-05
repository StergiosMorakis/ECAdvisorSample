IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Ratings' and xtype='U')

	CREATE TABLE [dbo].[Ratings](
		[Id] [int] IDENTITY(1,1) NOT NULL,
		[SourceId] [int] NOT NULL,
		[SourceType] [varchar](24) NOT NULL,
		[ProductSuggestedId] [int] NOT NULL,
		[Experiment] [varchar](24) NOT NULL,
		[Rating] [int] NOT NULL,
		[UserId] [int] NOT NULL,
		[Date] [datetime] NULL,
		[SuggestionId] [int] NOT NULL,
	 CONSTRAINT [PK__Rat__3214EC071DC60E74] PRIMARY KEY CLUSTERED 
	(
		[Id] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY]

